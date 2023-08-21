# Standard libraries
import sys

# My libraries
import hand_utils

# Third-party libraries
import numpy as np
from sklearn.cluster import KMeans
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

class Hands:
    def __init__(self, clusters=2):
        self.right = dict()
        self.left = dict()
        self.kmeans = KMeans(n_clusters=clusters)
        self.coords_only = []
        self.rcop = [0,0]
        self.lcop = [0,0]

    def run_kmeans(self, Z, r=ROW_SIZE, c=COL_SIZE):

        # Creates a new array with the coordinates only of each point with a nonzero
        # reading from the pressure mat
        # 
        # Basically, to force kmeans to only consider the coordinates
        # of the points--not the sensor reading--when clustering.
        index = 0

        for row in range(r):
            for col in range(c):
                if Z[row][col]!=0:
                    self.coords_only.append([row, col])
                    #print("Appending: ", row, ",", col)
                    #print(Z[row][col])
                index+=1

        if not self.coords_only:
            return self.kmeans, []

        return self.kmeans.fit(self.coords_only), self.coords_only
    
    def isolate_hands(self, Z):


        index = 0
        right_index = 0
        left_index = 0
        for row in range(ROW_SIZE):
            for col in range(COL_SIZE):
                #print("Looking at: ", row, ",",col)
                if ([row, col] in self.coords_only):
                    if (self.kmeans.labels_[index] == 0): #right
                        #print("Adding to RIGHT\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                        self.right[(row, col)] = (Z[row][col])
                        right_index+=1
                    if (self.kmeans.labels_[index] == 1): #left
                        #print("Adding to LEFT\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                        self.left[(row, col)] = (Z[row][col])
                        left_index+=1
                    index+=1

        return self.right, self.left
    
    def generate_cops(self, h1, h2):
        cop1 = hand_utils.calculate_cop(h1)
        cop2 = hand_utils.calculate_cop(h2)

        #print("cop1: ", cop1)
        #print("cop2: ", cop2)

        if(cop1[0] < cop2[0]): #h1 is left hand
            #print("h1 is LEFT hand")
            self.rcop = h2
            self.lcop = h1
            return self.rcop, self.lcop, h2, h1
        
        #otherwise h1 is right hand
        else:
            #print("h1 is RIGHT hand")
            self.rcop = h1
            self.lcop = h2
            return self.rcop, self.lcop, h1, h2
        
class Hand_metadata:
    def __init__(self, hands: Hands):
        self.hands = hands
        self.cop = [0,0]
        self.ideal_cop = [0,0]
        self.correction_vector = [0.0, 0.0]
        self.actuators = {"i": False, "t": False, "w": False, "p": False}

    def generate_cops(self, h1, h2):

        both_hands = dict()
        both_hands.update(h1)
        both_hands.update(h2)
        self.cop = hand_utils.calculate_cop(both_hands)

        ideal_hands = dict()
        for k in both_hands.keys():
            ideal_hands[k] = 1
        self.ideal_cop = hand_utils.calculate_cop(ideal_hands)

        return self.ideal_cop, self.cop
    
    def find_correction_vector(self):
        self.correction_vector = hand_utils.create_vector(self.cop, self.ideal_cop)
        return self.correction_vector
    
    # quadrant determines which actuators to activate
#                 I
#     acx > icx   |  acx < icx
#     acy < icy   |  acy < icy
# P --------------•--------------- T
#     acx > icx   |  acx < icx
#     acy > icy   |  acy > icy
#                 W
def select_actuators(self):
    if(self.vector[0] >= 0 and self.vector[1] >= 0): #top right (IT)
        self.actuators['i'] = True
        self.actuators['t'] = True
        self.actuators['w'] = False
        self.actuators['p'] = False
    elif(self.vector[0] >= 0 and self.vector[1] <= 0): #bottom right (TW)
        self.actuators['i'] = False
        self.actuators['t'] = True
        self.actuators['w'] = True
        self.actuators['p'] = False
    elif(self.vector[0] <= 0 and self.vector[1] <= 0): #bottom left (WP)
        self.actuators['i'] = False
        self.actuators['t'] = False
        self.actuators['w'] = True
        self.actuators['p'] = True
    elif(self.vector[0] <= 0 and self.vector[1] >= 0): #top left (PI)
        self.actuators['i'] = True
        self.actuators['t'] = False
        self.actuators['w'] = False
        self.actuators['p'] = True

    return self.actuators

