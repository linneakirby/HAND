# Standard libraries
import sys
import time

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
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'

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
        
    return app, data

def sendRightHandDataToArduino(data):
    #if data is just mat values snapshot
    # used for testing without Mat object
    if isinstance(data, np.ndarray):
        a = process_mat_data(data)
    #if data is a Mat object -> used for normal HAND behavior
    if isinstance(data, Mat):
        data.get_matrix()
        print(data)
        a = process_mat_data(data.Values)
    return a

def sendLeftHandDataToArduino(data):
    #if data is just mat values snapshot
    # used for testing without Mat object
    if isinstance(data, np.ndarray):
        a = process_mat_data(data)
    #if data is a Mat object -> used for normal HAND behavior
    if isinstance(data, Mat):
        data.get_matrix()
        print(data)
        a = process_mat_data(data.Values)
    return a

def process_mat_data(d):
    h = Hands()
    if np.any(d):
        h.run_kmeans(d)
        h.isolate_hands(d)
        h.generate_cops()
        h.find_correction_vector()
        print(f"CoP: {h.cop} - ideal {h.ideal_cop}")
        h.select_actuators()
    values = str(h.get_actuators())
    print(f"Actuator: {values}")
    return values

if __name__ == '__main__':
    app, data = create_app()
    app.run(host='0.0.0.0', port=8090, threaded=True)
    # time.sleep(0.1) # not sure if server should sleep or if it should all be on the gloves' end