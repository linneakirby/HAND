# Standard libraries
import subprocess
import sys
import time

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
import serial.tools.list_ports
import skimage



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

    def RequestPressureMap(self):
        data = "R"
        self.ser.write(data.encode())

    def activePointsReceiveMap(self):
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
    
    def activePointsGetMap(self):
        xbyte = ''
        if self.ser.in_waiting > 0:
            try:
                xbyte = self.ser.read().decode('utf-8')
            except Exception:
                print("Exception")
            if(xbyte == 'N'):
                self.activePointsReceiveMap()
            else:
                self.ser.flush()

    def getMatrix(self):
        self.RequestPressureMap()
        self.activePointsGetMap()
    
    def plotMatrix(self):
        tmparray = np.zeros((ROWS, COLS))
        for i in range(COLS):
            tmp = ""
            for j in range(ROWS):
                tmp = int(self.Values[i][j])
                tmparray[i][j] = tmp
        generatePlot(tmparray)

    def printMatrix(self):
        for i in range(COLS):
            tmp = ""
            for j in range(ROWS):
                tmp = tmp +   hex(int(self.Values[i][j]))[-1]
            print(tmp)
        print("\n")

def getPort():
    # This is how serial ports are organized on macOS.
    # You may need to change it for other operating systems.
    print("Getting ports")
    ports = list(serial.tools.list_ports.grep("\/dev\/cu.usbmodem[0-9]{9}"))
    return ports[0].device


def generatePlot(Z):
    plt.ion()
    fig, ax = plt.subplots(figsize=(5,5))

    ax.contourf(np.arange(0, ROWS), np.arange(0, COLS), Z, levels=7, cmap="nipy_spectral")

    plt.draw()
    # plt.savefig(FIG_PATH)
    # plt.pause(0.0001)
    # plt.clf()

#run k clustering on self.Values: https://realpython.com/k-means-clustering-python/#how-to-perform-k-means-clustering-in-python
#visualize which points are in which cluster
#then can do center of mass calculation: https://stackoverflow.com/questions/29356825/python-calculate-center-of-mass


def main():
    mat = Mat(getPort())
    while True:
        mat.getMatrix()
        if not CONTOUR:
            mat.printMatrix()
        if CONTOUR:
            mat.plotMatrix()
        time.sleep(0.1)

if __name__ == '__main__':
    main()