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
CONTOUR = True
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
    

    def plot_matrix(self):
        two_d_array = ndarray_to_2darray(self.Values)
        k_means(self.Values)
        generate_plot(two_d_array)

    def print_matrix(self):
        for i in range(COLS):
            tmp = ""
            for j in range(ROWS):
                tmp = tmp +   hex(int(self.Values[i][j]))[-1]
            print(tmp)
        print("\n")



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

def remove_empty_points(nda):
    tda = [[],[]]
    for i in range(48):
        for j in range(48):
            if(int(nda[i][j]) != 0):
                tda[0].append(i)
                tda[1].append(j)
    return tda

#run k clustering on self.Values: https://realpython.com/k-means-clustering-python/#how-to-perform-k-means-clustering-in-python
def k_means(karray, clusters=2):
    kmeans = KMeans(init="k-means++", n_clusters=clusters, n_init=10, max_iter=300, random_state=42)
    return kmeans.fit(karray)

def generate_kmeans_plot(karray, clusters=2):
    tda = remove_empty_points(karray)
    km = k_means(tda)
    y_km = km.fit_predict(tda)

    plt.scatter(
        tda[0], tda[1],
        s=50, c='lightgreen',
        marker='v', edgecolor='black',
        label='cluster 1'
    )

    # plt.scatter(
    #     tda[y_km == 1, 0], tda[y_km == 1, 1],
    #     s=50, c='orange',
    #     marker='o', edgecolor='black',
    #     label='cluster 2'
    # )

    plt.legend(scatterpoints=1)
    plt.grid()
    plt.show()

def generate_plot(Z):
    plt.ion()
    fig, ax = plt.subplots(figsize=(5,5))

    ax.contourf(np.arange(0, ROWS), np.arange(0, COLS), Z, levels=7, cmap="nipy_spectral")

    plt.draw()
    # plt.savefig(FIG_PATH)
    # plt.pause(0.0001)
    # plt.clf()


#visualize which points are in which cluster
#then can do center of mass calculation: https://stackoverflow.com/questions/29356825/python-calculate-center-of-mass


def main():
    mat = Mat(get_port())
    while True:
        mat.get_matrix()
        if not CONTOUR:
            mat.print_matrix()
        if CONTOUR:
            mat.plot_matrix()
        time.sleep(0.1)

if __name__ == '__main__':
    main()