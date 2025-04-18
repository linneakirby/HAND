# Standard libraries
import sys
import time
import os

# My libraries
from Mat import *
from Hands import *
import hand_utils

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
from flask import Flask

# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
DEFAULT_FOLDER = './Results/Sequence'+str(time.time_ns())
SAVE_SEQUENCE = False
TEST = True
LIVEMAT = False

def create_app(data = None):
    app = Flask(__name__)
    if data is None: #if no mat values provided
        data = Mat(hand_utils.get_port())

    @app.route('/rhand')
    def rhand():
        return sendRightHandDataToArduino(data)
    
    @app.route('/lhand')
    def lhand():
        return sendLeftHandDataToArduino(data)
    
    @app.route('/hand')
    def hand():
        return sendDataToArduino(data)
        
    #data.printMatrix()
    return app, data

def sendDataToArduinoHelper(data):
    #if data is just mat values snapshot
    # used for testing without Mat object
    if isinstance(data, np.ndarray):
        a = process_mat_data(data)
    #if data is a Mat object -> used for normal HAND behavior
    if isinstance(data, Mat):
        data.get_matrix()
        data.printMatrix()
        a = process_mat_data(data.Values)
    return a

# process both hands
def sendDataToArduino(data):
    a = sendDataToArduinoHelper(data)
    return str(a)

def sendRightHandDataToArduino(data):
    a = sendDataToArduinoHelper(data)
    return a.r_str()

def sendLeftHandDataToArduino(data):
    a = sendDataToArduinoHelper(data)
    return a.l_str()

def process_mat_data(d):
    h = Hands()
    if np.any(d):
        h.run_kmeans(d)
        h1_bounds, h2_bounds = h.isolate_hands(d)
        h.generate_cops(h1_bounds, h2_bounds)
        h.find_correction_vector()
        #print(f"CoP: {h.cop} - ideal {h.ideal_cop}")
        h.select_actuators()
    #return actuators
    return h.get_actuators()

if __name__ == '__main__':
    print("Welcome to Haptic Assisted iNversions Device (HAND)")
    print("Ctrl+C to exit")

    try:
        if(TEST):
            if LIVEMAT:
                print("TESTING LIVE MAT")
                m = Mat(hand_utils.get_port())
                while(True):
                    sendDataToArduino(m)
                    time.sleep(0.1)

            else:
                hands_array = np.load(os.getcwd() + "/Testing/hands_rot.npy")
                m = Mat(hands_array)
                app, data = create_app(hands_array)
                m.printMatrix()
                m.plotMatrix()
                time.sleep(1)
                app.run(host='0.0.0.0', port=8090, threaded=True)
        else:
            app, data = create_app()
            app.run(host='0.0.0.0', port=8090, threaded=True)
            # TODO: save sequences in live
            # can only draw in main thread, so it only saves the first snapshot
            if SAVE_SEQUENCE:
                if not os.path.exists(DEFAULT_FOLDER):
                    os.makedirs(DEFAULT_FOLDER+'/plot')
                    os.makedirs(DEFAULT_FOLDER+'/data')

                data.plotMatrix(fp=DEFAULT_FOLDER+'/plot/contour'+str(time.time_ns())+'.png')
                np.save(DEFAULT_FOLDER+'/data/data'+str(time.time_ns())+'.npy', data.Values)
            # time.sleep(0.1) # not sure if server should sleep or if it should all be on the gloves' end
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")