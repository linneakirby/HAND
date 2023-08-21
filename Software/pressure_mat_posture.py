# Standard libraries
import sys
import time

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
from sklearn.cluster import KMeans
np.set_printoptions(threshold=sys.maxsize)
from flask import Flask

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

CONSOLE = False
CONTOUR = True
SCATTER = False
HEAT = False

if CONTOUR:
    plt.style.use('_mpl-gallery-nogrid')

class Mat:
    def __init__(self, port):
        self.ser = serial.Serial(
            port,
            baudrate=115200,
            timeout=0.1)
        self.Values = np.zeros((ROW_SIZE, COL_SIZE))

    def request_pressure_map(self):
        data = "R"
        self.ser.write(data.encode())

    def active_points_receive_map(self):
        matrix = np.zeros((ROW_SIZE, COL_SIZE), dtype=int)

        xbyte = self.ser.read().decode('utf-8')

        HighByte = self.ser.read()
        LowByte = self.ser.read()
        high = int.from_bytes(HighByte, 'big')
        low = int.from_bytes(LowByte, 'big')
        nPoints = ((high << 8) | low)

        xbyte = self.ser.read().decode('utf-8')
        xbyte = self.ser.read().decode('utf-8')
        x = 0
        y = 0
        n = 0
        while(n < nPoints):
            x = self.ser.read()
            y = self.ser.read()
            x = int.from_bytes(x, 'big')
            y = int.from_bytes(y, 'big')
            HighByte = self.ser.read()
            LowByte = self.ser.read()
            high = int.from_bytes(HighByte, 'big')
            low = int.from_bytes(LowByte, 'big')
            val = ((high << 8) | low)
            matrix[y][x] = val
            n += 1
        self.Values = matrix
    
    def active_points_get_map(self):
        xbyte = ''
        if self.ser.in_waiting > 0:
            try:
                xbyte = self.ser.read().decode('utf-8')
            except Exception:
                print("Exception")
            if(xbyte == 'N'):
                self.active_points_receive_map()
            else:
                self.ser.flush()

    def get_matrix(self):
        self.request_pressure_map()
        self.active_points_get_map()
    
    def separate_hands(self):
        Z = transform_matrix_180(self.Values)
        kmeans, coords_only = run_kmeans(Z)
        return Z, kmeans, coords_only

    def plot_matrix(self, contour=CONTOUR, scatter=SCATTER, heat=HEAT):
        Z, kmeans, coords_only = self.separate_hands()
        right, left = self.isolate_hands(Z, kmeans, coords_only)
        rcop, lcop, ideal_cop, actual_cop = self.center_of_pressure(right, left)

        # decide what visualizations to show
        if(contour):
            two_d_array = ndarray_to_2darray(Z)
            generate_contour_plot(two_d_array)
        if(scatter):
            generate_scatter_plot(kmeans, coords_only)
        if(heat):
            generate_heatmap_plot(Z)

    def print_matrix(self):
        for i in range(COL_SIZE):
            tmp = ""
            for j in range(ROW_SIZE):
                tmp = tmp +   hex(int(self.Values[i][j]))[-1]
            print(tmp)
        print("\n")

# 180 degree transformation - may need to also have a function for -90 degree transformation
def transform_matrix_180(Z):
    # copy and shift matrix
    matrix_dict = dict()
    for row in range(ROW_SIZE):
        for col in range(COL_SIZE):
            matrix_dict[(row-ROW_SIZE//2, col-COL_SIZE//2)] = Z[row][col]
    # rotate matrix
    rotated_dict = dict()
    for point in matrix_dict:
        x = -point[0]
        y = -point[1]
        rotated_dict[(x,y)] = matrix_dict[point]

    # shift matrix back and reconstruct ndarray
    ret_matrix = np.zeros((ROW_SIZE, COL_SIZE), dtype=int)
    for point in rotated_dict:
        ret_matrix[point[0]+ROW_SIZE//2-1][point[1]+COL_SIZE//2-1] = rotated_dict[point]
    return ret_matrix


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

def generate_contour_plot(Z):
    plt.ion()
    fig, ax = plt.subplots(figsize=(5,5))

    ax.contourf(np.arange(0, ROW_SIZE), np.arange(0, COL_SIZE), Z, levels=7, cmap="nipy_spectral")

    plt.draw()
    # plt.savefig(FIG_PATH)
    # plt.pause(0.0001)
    # plt.clf()

def generate_heatmap_plot(Z):
    plt.imshow(Z, cmap='inferno', interpolation='nearest')
    plt.show()

#run k clustering on self.Values: https://realpython.com/k-means-clustering-python/#how-to-perform-k-means-clustering-in-python
def run_kmeans(Z, clusters=2, r=ROW_SIZE, c=COL_SIZE):
    kmeans = KMeans(n_clusters=clusters)

    # Creates a new array with the coordinates only of each point with a nonzero
    # reading from the pressure mat
    # 
    # Basically, to force kmeans to only consider the coordinates
    # of the points--not the sensor reading--when clustering.
    coords_only = []
    index = 0

    for row in range(r):
        for col in range(c):
            if Z[row][col]!=0:
                coords_only.append([row, col])
                #print("Appending: ", row, ",", col)
                #print(Z[row][col])
            index+=1

    if not coords_only:
        return kmeans, []

    return kmeans.fit(coords_only), coords_only

def isolate_hands(Z, kmeans, coords_only):

    h1 = dict()
    h2 = dict()

    index = 0
    h1_index = 0
    h2_index = 0
    for row in range(ROW_SIZE):
        for col in range(COL_SIZE):
            #print("Looking at: ", row, ",",col)
            if ([row, col] in coords_only):
                if (kmeans.labels_[index] == 0): #right
                    #print("Adding to h1\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                    h1[(row, col)] = (Z[row][col])
                    h1_index+=1
                if (kmeans.labels_[index] == 1): #left
                    #print("Adding to h2\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                    h2[(row, col)] = (Z[row][col])
                    h2_index+=1
                index+=1

    return h1, h2

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

def generate_cops(h1, h2):

    both_hands = dict()
    both_hands.update(h1)
    both_hands.update(h2)
    actual_cop = calculate_cop(both_hands)

    ideal_hands = dict()
    for k in both_hands.keys():
        ideal_hands[k] = 1
    ideal_cop = calculate_cop(ideal_hands)

    cop1 = calculate_cop(h1)
    cop2 = calculate_cop(h2)

    #print("cop1: ", cop1)
    #print("cop2: ", cop2)

    if(cop1[0] < cop2[0]): #h1 is left hand
        #print("h1 is LEFT hand")
        return cop2, cop1, ideal_cop, actual_cop, h2, h1
    
    #otherwise h1 is right hand
    else:
        #print("h1 is RIGHT hand")
        return cop1, cop2, ideal_cop, actual_cop, h1, h2


def create_actuator_dict():
    actuators = dict()
    actuators['i'] = False #index
    actuators['p'] = False #pinky
    actuators['w'] = False #wrist
    actuators['t'] = False #thumb

    return actuators

def create_vector(start, end):
    return (end[0]-start[0], end[1]-start[1])

# actual_cop is origin
# subtract actual_cop from ideal_cop
# quadrant determines which actuators to activate
#                 I
#     acx > icx   |  acx < icx
#     acy < icy   |  acy < icy
# P --------------•--------------- T
#     acx > icx   |  acx < icx
#     acy > icy   |  acy > icy
#                 W
def select_actuators(vector, actuators):
    if(vector[0] >= 0 and vector[1] >= 0): #top right (IT)
        actuators['i'] = True
        actuators['t'] = True
        actuators['w'] = False
        actuators['p'] = False
    elif(vector[0] >= 0 and vector[1] <= 0): #bottom right (TW)
        actuators['i'] = False
        actuators['t'] = True
        actuators['w'] = True
        actuators['p'] = False
    elif(vector[0] <= 0 and vector[1] <= 0): #bottom left (WP)
        actuators['i'] = False
        actuators['t'] = False
        actuators['w'] = True
        actuators['p'] = True
    elif(vector[0] <= 0 and vector[1] >= 0): #top left (PI)
        actuators['i'] = True
        actuators['t'] = False
        actuators['w'] = False
        actuators['p'] = True

    return actuators

def generate_scatter_plot(kmeans, coords_only, rcop, lcop, ideal_cop, actual_cop, figure, r=ROW_SIZE, c=COL_SIZE):
    # TODO: refactor this so it uses the left and right dicts
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


def print_ascii(matrix):
        for j in range(COL_SIZE-1, -1, -1):
            tmp = ""
            for i in range(ROW_SIZE):
                tmp = tmp +   hex(int(matrix[i][j]))[-1]
            print(tmp)
        print("\n")


def execute_instructions(hands_array, figure):
    parameters_dict = dict()
    tm = hands_array
    tm = np.rot90(hands_array, 2) # make it right-side up


    kmeans, coords_only = run_kmeans(tm)

    if(coords_only):

        h1, h2 = isolate_hands(tm, kmeans, coords_only)

        actual_rcop, actual_lcop, ideal_cop, actual_cop, r, l = generate_cops(h1, h2)

        actuators = create_actuator_dict()

        vector = create_vector(actual_cop, ideal_cop)

        actuators = select_actuators(vector, actuators)

        generate_scatter_plot(kmeans, coords_only, actual_rcop, actual_lcop, ideal_cop, actual_cop, figure)

        parameters_dict["kmeans"] = kmeans
        parameters_dict["coords"] = coords_only
        parameters_dict["r"] = r
        parameters_dict["l"] = l
        parameters_dict["rcop"] = actual_rcop
        parameters_dict["lcop"] = actual_lcop
        parameters_dict["icop"] = ideal_cop
        parameters_dict["cop"] = actual_cop
        parameters_dict["a"] = actuators
        parameters_dict["v"] = vector

    return parameters_dict

def main():
    mat = Mat(get_port())
    mat.get_matrix()
    if CONSOLE:
        mat.print_matrix()
        
    fig, ax = plt.subplots(figsize=(5,5))
    plt.ion()
    execute_instructions(mat.Values, fig)
    plt.show()
    time.sleep(0.1)

if __name__ == '__main__':
    main()