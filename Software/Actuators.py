# Standard libraries
import sys

# Third-party libraries
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

class Actuator:
    def __init__(self):
        self.is_on = False
        self.magnitude = 0.0

    def __str__(self):
        s = ""
        if not self.is_on:
            s = s + "not "
        s = s + "on with a magnitude of " + str(self.magnitude)
        return s

    def turn_on(self, m=1.0):
        self.is_on = True
        self.magnitude = m

    def turn_off(self):
        self.is_on = False
        self.magnitude = 0.0

    def adjust_magnitude(self, m):
        self.magnitude = m

    def reset(self):
        self.is_on = False
        self.magnitude = 0.0

    def get_magnitude(self):
        return self.magnitude
    
    def is_on(self):
        return self.is_on
    
class Actuator_manager:
    def __init__(self):
        self.index = Actuator()
        self.right = Actuator()
        self.wrist = Actuator()
        self.left = Actuator()

    def __str__(self):
        s = "Index " + str(self.index) + "\n" #add index actuator
        s = s + "Right " + str(self.right) + "\n" #add right actuator
        s = s + "Wrist " + str(self.wrist) + "\n" #add wrist actuator
        s = s + "Left " + str(self.left) #add left actuator
        return s
    
    def activate_index(self):
        self.index.turn_on()
        self.wrist.turn_off()

    def activate_right(self):
        self.right.turn_on()
        self.left.turn_off()

    def activate_wrist(self):
        self.wrist.turn_on()
        self.wrist.turn_off()

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
