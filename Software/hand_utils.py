# Standard libraries
import sys

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'

def get_port():
    # This is how serial ports are organized on macOS.
    # You may need to change it for other operating systems.
    print("Getting ports")
    ports = list(serial.tools.list_ports.grep("\/dev\/cu.usbmodem[0-9]{9}"))
    return ports[0].device

def ndarray_to_2darray(nda, preserve_values=True, r=ROW_SIZE, c=COL_SIZE):
    two_d_array = np.zeros((r, c))
    for i in range(c):
        tmp = ""
        for j in range(r):
            if(preserve_values):
                tmp = int(nda[i][j])
                two_d_array[i][j] = tmp
            else:
                if(int(nda[i][j]) != 0):
                    two_d_array[i][j] = 1
    return two_d_array

# based off of http://hyperphysics.phy-astr.gsu.edu/hbase/cm.html
def calculate_cop(pv_dict):
    cop = [0,0]

    for k in pv_dict.keys():
        cop[0] = cop[0] + k[0]*pv_dict.get(k)
        cop[1] = cop[1] + k[1]*pv_dict.get(k)
        #print("MULTIPLIED BY: ", pv_dict.get(k))
        #print("COP IS NOW: ", cop[0], ",", cop[1])

    for i in range(2):
        cop[i] = cop[i]/sum(pv_dict.values())

    #print("COP IS RETURNING AS: ", cop[0], ",", cop[1])
    return cop

def create_vector(start, end):
    return (end[0]-start[0], end[1]-start[1])

def generate_scatter_plot(kmeans, coords_only, rcop, lcop, ideal_cop, actual_cop, figure, r=ROW_SIZE, c=COL_SIZE):
    index = 0
    for row in range(r):
        for col in range(c):
            if [row, col] in coords_only:
                if kmeans.labels_[index] == 1:
                    plt.scatter(
                        row, col,
                        s=40, c='orange',
                        marker='o', edgecolor='black'
                    )
                if kmeans.labels_[index] == 0:
                    plt.scatter(
                        row, col,
                        s=40, c='violet',
                        marker='v', edgecolor='black'
                    )
                index+=1

    # add center of pressure markers
    plt.scatter(
        rcop[0], rcop[1],
        s=60, c='orangered',
        marker='s', edgecolor='lime', label='right CoP'
        )
    plt.scatter(
        lcop[0], lcop[1],
        s=60, c='indigo',
        marker='s', edgecolor='lime', label='left CoP'
        )
    plt.scatter(
        ideal_cop[0], ideal_cop[1],
        s=60, c='dodgerblue',
        marker='s', edgecolor='lime', label='ideal CoP'
        )
    plt.scatter(
        actual_cop[0], actual_cop[1],
        s=60, c='aquamarine',
        marker='s', edgecolor='lime', label='current CoP'
        )

    # add vector
    dx = ideal_cop[0] - actual_cop[0]
    dy = ideal_cop[1] - actual_cop[1]
    plt.arrow(actual_cop[0], actual_cop[1], dx, dy, facecolor = "red", edgecolor = "none", width=.2)

    # add legend
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), 
           ncol=5)

    #plt.legend(scatterpoints=1)
    # plt.grid()
    # plt.draw()
    #plt.show()
    figure.canvas.draw()
    figure.canvas.flush_events()