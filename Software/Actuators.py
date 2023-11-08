# Standard libraries
import sys

# Third-party libraries
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

class Actuator:
    def __init__(self):
        self.status = False
        self.magnitude = 0.0

    def __str__(self):
        s = ""
        s = s + str(self.magnitude)
        return s

    def turn_on(self, m=1.0):
        self.status = True
        self.magnitude = m

    def turn_off(self):
        self.status = False
        self.magnitude = 0.0

    def adjust_magnitude(self, m):
        self.magnitude = m

    def reset(self):
        self.status = False
        self.magnitude = 0.0

    def get_magnitude(self):
        return self.magnitude
    
    def is_on(self):
        return self.status
    
class Actuator_manager:
    def __init__(self):
        self.index = Actuator()
        self.right = Actuator()
        self.wrist = Actuator()
        self.left = Actuator()

    def __str__(self):
        s = str(self.index) + " " #add index actuator
        s = s + str(self.right) + " " #add right actuator
        s = s + str(self.wrist) + " " #add wrist actuator
        s = s + str(self.left) #add left actuator
        return s
    
    def activate_index(self):
        self.index.turn_on()
        self.wrist.turn_off()

    def activate_right(self):
        self.right.turn_on()
        self.left.turn_off()

    def activate_wrist(self):
        self.wrist.turn_on()
        self.index.turn_off()

    def activate_left(self):
        self.left.turn_on()
        self.right.turn_off()

    def deactivate_index(self):
        self.index.turn_off()

    def deactivate_right(self):
        self.right.turn_off()

    def deactivate_wrist(self):
        self.wrist.turn_off()

    def deactivate_left(self):
        self.left.turn_off()

    def reset(self):
        self.index.reset()
        self.right.reset()
        self.wrist.reset()
        self.left.reset()

    def get_index(self):
        return self.index
    
    def get_right(self):
        return self.right
    
    def get_wrist(self):
        return self.wrist
    
    def get_left(self):
        return self.left