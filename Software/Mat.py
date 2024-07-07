# Standard libraries
import sys

# Third-party libraries
import numpy as np
import serial.tools.list_ports
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

class Mat:
    def __init__(self, port):
        #if only a frame, i.e. for testing
        if isinstance(port, np.ndarray):
            self.Values = port
        else:
            self.ser = serial.Serial(
                port,
                baudrate=115200,
                timeout=0.1)
            self.Values = np.zeros((ROWS, COLS))

    def request_pressure_map(self):
        data = "R"
        print(f"N bytes written: {self.ser.write(data.encode())}")

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

    def printMatrix(self, c=COLS, r=ROWS):
        for x in range(c): #x
            tmp = ""
            for y in range(r): #y
                tmp = tmp +   hex(int(self.Values[x][y]))[-1]
            print(tmp)
        print("\n")


    def __str__(self):
        s = ""
        for x in range(COLS): #x
            tmp = ""
            for y in range(ROWS): #y
                tmp = tmp +   hex(int(self.Values[x][y]))[-1]
            s = s+tmp
            s = s+"\n"

        return s