# Standard libraries
import sys

# Third-party libraries
import numpy as np
import serial.tools.list_ports
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

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


    def __str__(self):
        s = ""
        for j in range(COL_SIZE-1, -1, -1):
            tmp = ""
            for i in range(ROW_SIZE):
                tmp = tmp +   hex(int(self.Values[i][j]))[-1]
            s = s+tmp
        s = s+"\n"

        return s