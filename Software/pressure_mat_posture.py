# Standard libraries
import subprocess
import sys
import time

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
import skimage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

CONSOLE = False
CONTOUR = False
SCATTER = True
HEAT = False

if CONTOUR:
    plt.style.use('_mpl-gallery-nogrid')

class Mat:
    def __init__(self, port):
        self.ser = serial.Serial(
            port,
            baudrate=115200,
            timeout=0.1)
        self.Values = np.zeros((ROWS, COLS))

    def request_pressure_map(self):
        data = "R"
        self.ser.write(data.encode())

    def active_points_receive_map(self):
        matrix = np.zeros((ROWS, COLS), dtype=int)

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

    def isolate_hands(self, Z, kmeans, coords_only):
        right = dict()
        left = dict()

        index = 0
        for row in range(ROWS):
            for col in range(COLS):
                if [row, col] in coords_only:
                    if kmeans.labels_[index] == 1: #right
                        right[(row, col)] = Z[row][col]
                    if kmeans.labels_[index] == 0: #left
                        left[(row, col)] = Z[row][col]
                    index+=1

        return right, left

    def calculate_center_of_pressure(self, hand):
        cop = [0,0,0]

        for k in hand.keys():
            cop[0] = cop[0] + k[0]
            cop[1] = cop[1] + k[1]
            cop[2] = cop[2] + hand.get(k)

        for i in range(3):
            cop[i] = cop[i]/len(hand)

        return cop

    def center_of_pressure(self, right, left):
        rcop = self.calculate_center_of_pressure(right)
        lcop = self.calculate_center_of_pressure(left)

        cop = [0,0,0]
        for i in range(3):
            cop[i] = (rcop[i] + lcop[i]) / 2

        return rcop, lcop, cop

    def plot_matrix(self, contour=CONTOUR, scatter=SCATTER, heat=HEAT):
        Z, kmeans, coords_only = self.separate_hands()
        right, left = self.isolate_hands(Z, kmeans, coords_only)
        rcop, lcop, cop = self.center_of_pressure(right, left)

        # decide what visualizations to show
        if(contour):
            two_d_array = ndarray_to_2darray(Z)
            generate_contour_plot(two_d_array)
        if(scatter):
            generate_scatter_plot(kmeans, coords_only)
        if(heat):
            generate_heatmap_plot(Z)

    def print_matrix(self):
        for i in range(COLS):
            tmp = ""
            for j in range(ROWS):
                tmp = tmp +   hex(int(self.Values[i][j]))[-1]
            print(tmp)
        print("\n")

# 180 degree transformation - may need to also have a function for -90 degree transformation
def transform_matrix_180(Z):
    # copy and shift matrix
    matrix_dict = dict()
    for row in range(ROWS):
        for col in range(COLS):
            matrix_dict[(row-ROWS//2, col-COLS//2)] = Z[row][col]
    # rotate matrix
    rotated_dict = dict()
    for point in matrix_dict:
        x = -point[0]
        y = -point[1]
        rotated_dict[(x,y)] = matrix_dict[point]

    # shift matrix back and reconstruct ndarray
    ret_matrix = np.zeros((ROWS, COLS), dtype=int)
    for point in rotated_dict:
        ret_matrix[point[0]+ROWS//2-1][point[1]+COLS//2-1] = rotated_dict[point]
    return ret_matrix


def get_port():
    # This is how serial ports are organized on macOS.
    # You may need to change it for other operating systems.
    print("Getting ports")
    ports = list(serial.tools.list_ports.grep("\/dev\/cu.usbmodem[0-9]{9}"))
    return ports[0].device

def ndarray_to_2darray(nda, preserve_values=True):
    two_d_array = np.zeros((ROWS, COLS))
    for i in range(COLS):
        tmp = ""
        for j in range(ROWS):
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

    ax.contourf(np.arange(0, ROWS), np.arange(0, COLS), Z, levels=7, cmap="nipy_spectral")

    plt.draw()
    # plt.savefig(FIG_PATH)
    # plt.pause(0.0001)
    # plt.clf()

def generate_heatmap_plot(Z):
    plt.imshow(Z, cmap='inferno', interpolation='nearest')
    plt.show()

#run k clustering on self.Values: https://realpython.com/k-means-clustering-python/#how-to-perform-k-means-clustering-in-python
def run_kmeans(Z, clusters=2):
    kmeans = KMeans(n_clusters=clusters)

    # Creates a new array with the coordinates only of each point with a nonzero
    # reading from the pressure mat
    # 
    # Basically, to force kmeans to only consider the coordinates
    # of the points--not the sensor reading--when clustering.
    coords_only = []
    index = 0

    for row in range(ROWS):
        for col in range(COLS):
            if Z[row][col]!=0:
                coords_only.append([row, col])
            index+=1

    return kmeans.fit(coords_only), coords_only

def isolate_hands(Z, kmeans, coords_only):
    right = dict()
    left = dict()

    index = 0
    for row in range(ROWS):
        for col in range(COLS):
            if [row, col] in coords_only:
                if kmeans.labels_[index] == 1: #right
                    right[(row, col)] = Z[row][col]
                if kmeans.labels_[index] == 0: #left
                    left[(row, col)] = Z[row][col]
                index+=1

    return right, left

def calculate_center_of_pressure(hand):
    cop = [0,0,0]

    for k in hand.keys():
        cop[0] = cop[0] + k[0]
        cop[1] = cop[1] + k[1]
        cop[2] = cop[2] + hand.get(k)

    for i in range(3):
        cop[i] = cop[i]/len(hand)

    return cop

def center_of_pressure(right, left):
    rcop = calculate_center_of_pressure(right)
    lcop = calculate_center_of_pressure(left)

    cop = [0,0,0]
    for i in range(3):
        cop[i] = (rcop[i] + lcop[i]) / 2

    return rcop, lcop, cop

def generate_scatter_plot(kmeans, coords_only, rcop, lcop, cop):
    # TODO: refactor this so it uses the left and right dicts
    index = 0
    for row in range(ROWS):
        for col in range(COLS):
            if [row, col] in coords_only:
                if kmeans.labels_[index] == 1:
                    plt.scatter(
                        row, col,
                        s=50, c='orange',
                        marker='o', edgecolor='black',
                    )
                if kmeans.labels_[index] == 0:
                    plt.scatter(
                        row, col,
                        s=50, c='violet',
                        marker='v', edgecolor='black',
                    )
                index+=1

    plt.scatter(
        rcop[0], rcop[1],
        s=50, c='orangered',
        marker='s', edgecolor='lime', label='right CoP'
        )
    plt.scatter(
        lcop[0], lcop[1],
        s=50, c='indigo',
        marker='s', edgecolor='lime', label='left CoP'
        )
    plt.scatter(
        cop[0], cop[1],
        s=50, c='teal',
        marker='s', edgecolor='lime', label='CoP'
        )

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), 
           ncol=5)

    #plt.legend(scatterpoints=1)
    plt.grid()
    plt.show()

#visualize which points are in which cluster
#then can do center of mass calculation: https://stackoverflow.com/questions/29356825/python-calculate-center-of-mass


def main():
    mat = Mat(get_port())
    while True:
        mat.get_matrix()
        if CONSOLE:
            mat.print_matrix()
        mat.plot_matrix(contour=CONTOUR, scatter=SCATTER, heat=HEAT)
        time.sleep(0.1)

if __name__ == '__main__':
    main()