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

def init_hand_bounds():
    bounds = dict()
    bounds.setdefault("max x", ((-1, -1), 0))[0][0]
    bounds.setdefault("min x", ((50, 50), 0))[0][0]
    bounds.setdefault("max y", ((-1, -1), 0))[0][1]
    bounds.setdefault("min y", ((50, 50), 0))[0][1]
    return bounds

class Hand:
    def __init__(self):
        self.right = False
        self.left = False
        self.cop = [0, 0]
        self.bounds = init_hand_bounds()
        self.points = dict()

    def is_right(self):
        return self.right
    
    def is_left(self):
        return self.left
    
    def set_right(self, c=[0, 0], b=None):
        self.right = True
        self.left = False
        self.cop = c
        if b is None:
            self.bounds = init_hand_bounds()
        else:
            self.bounds = b

    def set_left(self, c=[0 ,0], b=None):
        self.right = False
        self.left = True
        self.cop = c
        if b is None:
            self.bounds = init_hand_bounds()
        else:
            self.bounds = b
    
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
    
    def get_bounds(self):
        return self.bounds

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

        for x in range(c): #x
            for y in range(r): #y
                if Z[y][x]!=0:
                    self.coords_only.append([x, y])
                    #print(Z[x][y])
                index+=1

        if not self.coords_only:
            return self.kmeans, []

        return self.kmeans.fit(self.coords_only), self.coords_only
    
    # should also ignore pressure values of 1
    # updates a hand's bounds with new point information
    def adjust_bounds(self, bounds, point, value):
        max_x = bounds.get("max x")[0][0]
        min_x = bounds.get("min x")[0][0]
        max_y = bounds.get("max y")[0][1]
        min_y = bounds.get("min y")[0][1]

        if (point[0] > max_x):
            bounds.update({"max x": (point, value)})
        if (point[0] < min_x):
            bounds.update({"min x": (point, value)})
        if (point[1] > max_y):
            bounds.update({"max y": (point, value)})
        if (point[1] < min_y):
            bounds.update({"min y": (point, value)})

    # isolates and separates hands
    # note that hands are UNORDERED
    def isolate_hands(self, Z):
        index = 0
        h1_index = 0
        h2_index = 0
        h1_bounds = init_hand_bounds()
        h2_bounds = init_hand_bounds()
        for x in range(COL_SIZE):
            for y in range(ROW_SIZE):
                #print("Looking at: ", x, ",",y)
                if ([x, y] in self.coords_only):
                    if (self.kmeans.labels_[index] == 0): #h1
                        #print("Adding to h1\nkey: ", x, ",", y, "\nvalue: ", Z[y][x])
                        self.h1.add_point((x, y), Z[y][x])
                        self.adjust_bounds(h1_bounds, (x, y), Z[y][x])
                        h1_index+=1
                    if (self.kmeans.labels_[index] == 1): #h2
                        #print("Adding to h2\nkey: ", x, ",", y, "\nvalue: ", Z[y][x])
                        self.h2.add_point((x, y), Z[y][x])
                        self.adjust_bounds(h2_bounds, (x, y), Z[y][x])
                        h2_index+=1
                    index+=1
        return h1_bounds, h2_bounds

    
    def generate_cops(self, h1_bounds, h2_bounds):
        cop1 = hand_utils.calculate_cop(self.h1.get_points())
        cop2 = hand_utils.calculate_cop(self.h2.get_points())

        if(cop1[0] < cop2[0]): #h1 is left hand
            self.h2.set_right(cop2, h2_bounds)
            self.h1.set_left(cop1, h1_bounds)
        
        #otherwise h1 is right hand
        else:
            self.h1.set_right(cop1, h1_bounds)
            self.h2.set_left(cop2, h2_bounds)

        both_hands = dict()
        both_hands.update(self.h1.get_points())
        both_hands.update(self.h2.get_points())
        #print("both hands: ")
        #print(both_hands)
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
    # x value -> aka left or right hand
    # if == 0 => activate both actuators to evenly shift towards index or wrist
    def select_actuators(self):
        li = False
        lw = False
        ri = False
        rw = False
        if(self.correction_vector[0] >= 0): #right
            ri, rw = self.check_y_value()
        if(self.correction_vector[0] <= 0): #left
            li, lw = self.check_y_value()
        self.actuators.set_right_status(ri, rw)
        self.actuators.set_left_status(li, lw)
        return self.actuators
    
    # y value -> aka index or wrist
    # if == 0 => activate both actuators to evenly shift to one side
    def check_y_value(self):
        i = False
        w = False
        if(self.correction_vector[1] <= 0): #index
            i = True
        if(self.correction_vector[1] >= 0): #wrist
            w = True
        return i, w

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
    
    def compile_bounds(self):
        # print("left hand bounds: ", self.get_left_hand().get_bounds())
        bounds = list()
        bounds.append(self.get_left_hand().get_bounds().get("max x"))
        bounds.append(self.get_left_hand().get_bounds().get("min x"))
        bounds.append(self.get_left_hand().get_bounds().get("max y"))
        bounds.append(self.get_left_hand().get_bounds().get("min y"))
        bounds.append(self.get_right_hand().get_bounds().get("max x"))
        bounds.append(self.get_right_hand().get_bounds().get("min x"))
        bounds.append(self.get_right_hand().get_bounds().get("max y"))
        bounds.append(self.get_right_hand().get_bounds().get("min y"))
        return bounds

    def get_bounds(self):
        return self.compile_bounds()