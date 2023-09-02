# Standard libraries
import sys

# My libraries
import hand_utils
from Actuators import *

# Third-party libraries
import numpy as np
from sklearn.cluster import KMeans
np.set_printoptions(threshold=sys.maxsize)

# Default parameters
ROW_SIZE = 48  # Rows of the sensor
COL_SIZE = 48  # Columns of the sensor
DEFAULT_PORT = '/dev/cu.usbmodem104742601'
FIG_PATH = './Results/contour.png'

class Hand:
    def __init__(self):
        self.right = False
        self.left = False
        self.cop = [0, 0]
        self.points = dict()

    def is_right(self):
        return self.right
    
    def is_left(self):
        return self.left
    
    def set_right(self, c=[0, 0]):
        self.right = True
        self.left = False
        self.cop = c

    def set_left(self, c=[0 ,0]):
        self.right = False
        self.left = True
        self.cop = c
    
    def get_cop(self):
        return self.cop
    
    def set_cop(self, c):
        self.cop = c

    def add_point(self, p, v):
        self.points[p] = v

    def remove_point(self, p):
        self.points.pop(p)

    def get_points(self):
        return self.points

class Hands:
    def __init__(self, clusters=2):
        #unordered hands
        self.h1 = Hand()
        self.h2 = Hand()
        self.kmeans = KMeans(n_clusters=clusters)
        self.coords_only = []
        self.ideal_cop = [0,0]
        self.correction_vector = [0.0, 0.0]
        self.actuators = Actuator_manager()

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
    
    # isolates and separates hands
    # note that hands are UNORDERED
    def isolate_hands(self, Z):
        index = 0
        h1_index = 0
        h2_index = 0
        for row in range(ROW_SIZE):
            for col in range(COL_SIZE):
                #print("Looking at: ", row, ",",col)
                if ([row, col] in self.coords_only):
                    if (self.kmeans.labels_[index] == 0): #h1
                        #print("Adding to h1\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                        self.h1.add_point((row, col), Z[row][col])
                        h1_index+=1
                    if (self.kmeans.labels_[index] == 1): #h2
                        #print("Adding to h2\nkey: ", row, ",", col, "\nvalue: ", Z[row][col])
                        self.h2.add_point((row, col), Z[row][col])
                        h2_index+=1
                    index+=1

    
    def generate_cops(self):
        cop1 = hand_utils.calculate_cop(self.h1.get_points())
        cop2 = hand_utils.calculate_cop(self.h2.get_points())

        if(cop1[0] < cop2[0]): #h1 is left hand
            self.h2.set_right(cop2)
            self.h1.set_left(cop1)
        
        #otherwise h1 is right hand
        else:
            self.h1.set_right(cop1)
            self.h2.set_left(cop2)

        both_hands = dict()
        both_hands.update(self.h1.get_points())
        both_hands.update(self.h2.get_points())
        self.cop = hand_utils.calculate_cop(both_hands)

        ideal_hands = dict()
        for k in both_hands.keys():
            ideal_hands[k] = 1
        self.ideal_cop = hand_utils.calculate_cop(ideal_hands)
    
    def find_correction_vector(self):
        self.correction_vector = hand_utils.create_vector(self.cop, self.ideal_cop)
        return self.correction_vector
    
    # quadrant vector lands in determines which actuators to activate
    #      I
    #      |  
    # L ---•--- R
    #      |  
    #      W
    def select_actuators(self):
        #x value
        if(self.correction_vector[0] >= 0): 
            self.actuators.activate_right()
        else:
            self.actuators.activate_left()

        #y value
        if(self.correction_vector[1] >= 0):
            self.actuators.activate_index()
        else:
            self.actuators.activate_wrist()

        return self.actuators
    
    def get_right_hand(self):
        if(self.h1.is_right()):
            return self.h1
        return self.h2
    
    def get_left_hand(self):
        if(self.h1.is_left()):
            return self.h1
        return self.h2
    
    def get_cop(self):
        return self.cop
    
    def get_ideal_cop(self):
        return self.ideal_cop
    
    def get_correction_vector(self):
        return self.correction_vector
    
    def get_actuators(self):
        return self.actuators

