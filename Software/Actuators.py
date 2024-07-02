# Standard libraries
import sys

# Third-party libraries
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

class Actuator:
    def __init__(self, n="none"):
        self.status = False
        self.magnitude = 0.0
        self.name = n

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
    
    def set_name(self, n):
        self.name = n
    
    def get_name(self):
        return self.name
    
class Actuator_manager:
    def __init__(self):
        # add right hand actuators
        self.r_index = Actuator("r_index")
        self.r_left = Actuator("r_left")
        self.r_wrist = Actuator("r_wrist")
        self.r_right = Actuator("r_right")
        # add left hand actuators
        self.l_index = Actuator("l_index")
        self.l_left = Actuator("l_left")
        self.l_wrist = Actuator("l_wrist")
        self.l_right = Actuator("l_right")

    def __str__(self):
        # add right hand actuators
        s = str(self.r_index) + " " #add right hand index actuator
        s = s + str(self.r_left) + " " #add right hand left actuator
        s = s + str(self.r_wrist) + " " #add right hand wrist actuator
        s = s + str(self.r_right) + " " #add right hand right actuator
        # add left hand actuators
        s = s + str(self.l_index) + " " #add left hand index actuator
        s = s + str(self.l_left) + " " #add left hand left actuator
        s = s + str(self.l_wrist) + " " #add left hand wrist actuator
        s = s + str(self.l_right) + " " #add left hand right actuator
        return s
    
    def r_str(self):
        s = str(self.r_index) + " " #add right hand index actuator
        s = s + str(self.r_left) + " " #add right hand left actuator
        s = s + str(self.r_wrist) + " " #add right hand wrist actuator
        s = s + str(self.r_right) + " " #add right hand right actuator
        return s
    
    def l_str(self):
        s = str(self.l_index) + " " #add left hand index actuator
        s = s + str(self.l_left) + " " #add left hand left actuator
        s = s + str(self.l_wrist) + " " #add left hand wrist actuator
        s = s + str(self.l_right) + " " #add left hand right actuator
        return s

############# ACTIVATE ACTUATORS #############
    ### INDEX ###
    def activate_r_index(self):
        self.r_index.turn_on()
        self.r_wrist.turn_off()

    def activate_l_index(self):
        self.l_index.turn_on()
        self.l_wrist.turn_off()

    def activate_index(self):
        self.activate_r_index()
        self.activate_l_index()

    ### RIGHT ###
    def activate_r_right(self):
        self.r_right.turn_on()
        self.r_left.turn_off()

    def activate_l_right(self):
        self.l_right.turn_on()
        self.l_left.turn_off()

    def activate_right(self):
        self.activate_r_right()
        self.activate_l_right()

    ### WRIST ###
    def activate_r_wrist(self):
        self.r_wrist.turn_on()
        self.r_index.turn_off()

    def activate_l_wrist(self):
        self.l_wrist.turn_on()
        self.l_index.turn_off()

    def activate_wrist(self):
        self.activate_r_wrist()
        self.activate_l_wrist()

    ### LEFT ###
    def activate_r_left(self):
        self.r_left.turn_on()
        self.r_right.turn_off()

    def activate_l_left(self):
        self.l_left.turn_on()
        self.l_right.turn_off()

    def activate_left(self):
        self.activate_r_left()
        self.activate_l_left()

############# DEACTIVATE ACTUATORS #############
    ### INDEX ###
    def deactivate_r_index(self):
        self.r_index.turn_off()

    def deactivate_l_index(self):
        self.l_index.turn_off()

    def deactivate_index(self):
        self.deactivate_r_index()
        self.deactivate_l_index()

    ### RIGHT ###
    def deactivate_r_right(self):
        self.r_right.turn_off()

    def deactivate_l_right(self):
        self.l_right.turn_off()

    def deactivate_right(self):
        self.deactivate_r_right()
        self.deactivate_l_right()

    ### WRIST ###
    def deactivate_r_wrist(self):
        self.r_wrist.turn_off()

    def deactivate_l_wrist(self):
        self.l_wrist.turn_off()

    def deactivate_wrist(self):
        self.deactivate_r_wrist()
        self.deactivate_l_wrist()

    ### LEFT ###
    def deactivate_r_left(self):
        self.r_left.turn_off()

    def deactivate_l_left(self):
        self.r_left.turn_off()

    def deactivate_left(self):
        self.deactivate_r_left()
        self.deactivate_l_left()

############# RESET ACTUATORS #############
    def reset(self):
        self.r_index.reset()
        self.r_left.reset()
        self.r_wrist.reset()
        self.r_right.reset()
        self.l_index.reset()
        self.l_left.reset()
        self.l_wrist.reset()
        self.l_right.reset()

############# GET ACTUATORS #############
    ### BY HAND ###
    def get_r_actuators(self):
        return [self.r_index, self.r_left, self.r_wrist, self.r_right]

    def get_l_actuators(self):
        return [self.l_index, self.l_left, self.l_wrist, self.l_right]

    ### INDEX ###
    def get_r_index(self):
        return self.r_index
    
    def get_l_index(self):
        return self.l_index

    def get_index(self):
        return self.get_r_index(), self.get_l_index()
    
    ### RIGHT ###
    def get_r_right(self):
        return self.r_right
    
    def get_l_right(self):
        return self.l_right
    
    def get_right(self):
        return self.get_r_right(), self.get_l_right()
    
    ### WRIST ###
    def get_r_wrist(self):
        return self.r_wrist
    
    def get_l_wrist(self):
        return self.l_wrist
    
    def get_wrist(self):
        return self.get_r_wrist(), self.get_l_wrist()
    
    ### LEFT ###
    def get_r_left(self):
        return self.r_left
    
    def get_l_left(self):
        return self.l_left
    
    def get_left(self):
        return self.get_r_left(), self.get_l_left()