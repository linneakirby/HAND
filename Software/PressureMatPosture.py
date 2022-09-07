# Standard libraries
import subprocess
import sys
import time

# Third-party libraries
import cv2
import matplotlib.pyplot as plt
import numpy as np
import serial


# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor
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

    def request_pressure_data(self):
        data = 'R'
        self.ser.write(data.encode())

    def read_pressure_data(self):
        matrix = np.zeros((ROWS, COLS), dtype=int)
        _ = self.ser.read().decode('utf-8')
        high_byte = self.ser.read()
        low_byte = self.ser.read()
        high = int.from_bytes(high_byte, 'big')
        low = int.from_bytes(low_byte, 'big')
        num_points = ((high << 8) | low)
        _ = self.ser.read().decode('utf-8')
        _ = self.ser.read().decode('utf-8')
        x = y = n = 0
        while n < num_points:
            x = self.ser.read()
            y = self.ser.read()
            x = int.from_bytes(x, 'big')
            y = int.from_bytes(y, 'big')
            high_byte = self.ser.read()
            low_byte = self.ser.read()
            high = int.from_bytes(high_byte, 'big')
            low = int.from_bytes(low_byte, 'big')
            val = ((high << 8) | low)
            matrix[y][x] = val
            n += 1
        return matrix

    def get_pressure_data(self):
        xbyte = ''
        if self.ser.in_waiting > 0:
            xbyte = self.ser.read().decode('utf-8')
            if(xbyte == 'N'):
                return self.read_pressure_map()
            else:
                self.ser.flush()

    def get_pressure_map(self):
        self.request_pressure_data()
        return self.get_pressure_data()

    def print_matrix(self, data):
        for i in range(COLS):
            tmp = ''
            for j in range(ROWS):
                tmp = tmp + hex(int(data[i][j]))[-1]
            print(tmp)
        print('\n')

def getPort():
    # This is how serial ports are organized on macOS.
    # You may need to change it for other operating systems.
    print("Getting port")
    return serial.tools.list_ports.grep("\/dev\/(cu|tty).usbmodem[0-9]{9}")


def generatePlot(Z):
    plt.ion()
    fig, ax = plt.subplots(figsize=(5,5))

    ax.contourf(np.arange(0, ROWS), np.arange(0, COLS), Z, levels=7, cmap="nipy_spectral")

    plt.draw()
    plt.savefig(FIG_PATH)
    plt.pause(0.0001)
    plt.clf()

def getBlobs():
    # Read image
    im = cv2.imread(FIG_PATH, cv2.IMREAD_GRAYSCALE)

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 200


    # Filter by Area.
    params.filterByArea = True
    params.minArea = 1500

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.87
        
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    ver = (cv2.__version__).split('.')
    if int(ver[0]) < 3 :
        detector = cv2.SimpleBlobDetector(params)
    else : 
        detector = cv2.SimpleBlobDetector_create(params)


    # Detect blobs.
    keypoints = detector.detect(im)
    print("keypoints")
    print(keypoints)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob
    if(keypoints):
        im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # Show blobs
        cv2.imshow("Keypoints", im_with_keypoints)
        cv2.waitKey(0)

def getBlobs2():
    # read image through command line
    img = cv2.imread(FIG_PATH)

    # convert the image to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Grayscale", gray_image)
    # cv2.waitKey(0)

    # convert the grayscale image to binary image
    ret, thresh = cv2.threshold(gray_image,127,255,0)

    # find contours in the binary image
    # im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    im2, contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(img, (cX, cY), 5, (255, 255, 255), -1)
        cv2.putText(img, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # display the image
        cv2.imshow("Image", img)
        cv2.waitKey(0)

def main():
    mat = Mat(getPort())
    while True:
        data = mat.get_pressure_map()
        mat.print_matrix(data)
   
if __name__ == 'main':
    main()