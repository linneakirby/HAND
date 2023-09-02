# Standard libraries
import sys
import time

# My libraries
import Mat
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

app = Flask(__name__)
mat = Mat(hand_utils.get_port())

@app.route('/hand')
def sendDataToArduino():
    mat.get_matrix()
    a = process_mat_data(mat.Values)
    return a

def process_mat_data(d):
    h = Hands()
    h.run_kmeans(d)
    h.isolate_hands(d)
    h.generate_cops()
    h.find_correction_vector()
    h.select_actuators()
    return h.get_actuators()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
    time.sleep(0.1)