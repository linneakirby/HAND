# Standard libraries
import sys
import time

# My libraries
import Mat
import Hands
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

def main(CONSOLE=False):
    mat = Mat(hand_utils.get_port())
    mat.get_matrix()
    if CONSOLE:
        mat.print()
        
    fig, ax = plt.subplots(figsize=(5,5))
    plt.ion()
    #TODO: fix this here
    #execute_instructions(mat.Values, fig)
    plt.show()
    time.sleep(0.1)

if __name__ == '__main__':
    main()