# Standard libraries
import sys
import time

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
FIG_PATH = './Results/contour'+str(time.time)+'.png'

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

        if(cop1[1] < cop2[1]): #h1 is left hand
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
    
    # each hand represents L or R
    # within hand only I and W actuators
    # less granular than using 4
    # x value -> aka index or wrist
    # if == 0 => activate both actuators to evenly shift to one side
    def select_actuators(self):
        li = False
        lw = False
        ri = False
        rw = False
        if(self.correction_vector[0] >= 0): #wrist
            lw, rw = self.check_y_value()
        if(self.correction_vector[0] <= 0): #index
            li, ri = self.check_y_value()
        self.actuators.set_right_status(ri, rw)
        self.actuators.set_left_status(li, lw)
        return self.actuators
    
    # y value -> aka left or right hand
    # if == 0 => activate both actuators to evenly shift towards index or wrist
    def check_y_value(self):
        l = False
        r = False
        if(self.correction_vector[1] <= 0): #left
            l = True
        if(self.correction_vector[1] >= 0): #right
            r = True
        return l, r

    def set_right(self, index=False, wrist=False):
        self.actuators.set_right_status(index, wrist)

    def set_left(self, index=False, wrist=False):
        self.actuators.set_left_status(index, wrist)

    def deactivate_right(self):
        self.set_right(self)

    def deactivate_left(self):
        self.set_left(self)

    # quadrant vector lands in determines which actuators to activate
    #      I
    #      |  
    # L ---•--- R
    #      |  
    #      W
    # TODO: needs to be more granular to compare within hands COPs
    def select_actuators_by_hand(self):
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

