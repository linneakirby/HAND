# Standard libraries
import argparse
import sys
import time
import os

# My libraries
from Mat import *
from Hands import *
import hand_utils

# Third-party libraries
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
from flask import Flask
from pythonosc import udp_client

# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor
CONTOUR = True
DEFAULT_FOLDER = './Results/Sequence'+str(time.time_ns())
TEST = True
DATATYPE = 0 # 0 = actuators, 1 = bounds

def create_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  return args

#send a single instruction
def send_instruction(client, i):
  client.send_message("/hand", i)

#send a list of instructions
def send_instructions(client, i_list):
  client.send_message("/hand", i_list)

# make a copy an existing list
def copy_list(l):
  l2 = list()
  for i in l:
    l2.append(i)
  return l2

# add an instruction to a list of instructions
def add_instruction(i_list, i):
  p = copy_list(i_list)
  p.append(i)
  return p

def process_mat_data(d, ret_type=0):
    h = Hands()
    if np.any(d):
        h.run_kmeans(d)
        h1_bounds, h2_bounds = h.isolate_hands(d)
        h.generate_cops(h1_bounds, h2_bounds)
        h.find_correction_vector()
        #print(f"CoP: {h.cop} - ideal {h.ideal_cop}")
        h.select_actuators()
    if(ret_type == 1):
       #print("returning hand boundaries")
       return h.get_bounds(), h.get_correction_vector()
    #print("returning actuator values")
    return h.get_actuators(), h.get_correction_vector()

def process_data_helper(data, ret_type=0):
    #if data is just mat values snapshot
    # used for testing without Mat object
    if isinstance(data, np.ndarray):
      return process_mat_data(data, ret_type)
    #if data is a Mat object -> used for normal HAND behavior
    if isinstance(data, Mat):
      data.get_matrix()
      #print(data)
      values, vector = process_mat_data(data.Values, ret_type)
      if CONTOUR:
        if not os.path.exists(DEFAULT_FOLDER):
           os.makedirs(DEFAULT_FOLDER)
        data.plotMatrix(fp=DEFAULT_FOLDER+'/contour'+str(time.time_ns())+'.png')
      return values, vector

# process both hands
def process_data(data, ret_type=DATATYPE):
  values, vector = process_data_helper(data, ret_type)
  if(ret_type == 1): #returning hand boundaries
    #print("RETURNING HAND BOUNDARIES")
    return values, vector
  # otherwise must be returning actuators
  #print("RETURNING ACTUATORS")
  return values.get_actuator_list_2(), vector

def get_mat_data(data = None):
  if data is None: #if no mat values provided
      data = Mat(hand_utils.get_port())
  return data

def compile_instructions(list1, list2, list2_is_point_pressure_values=DATATYPE):
  ret = copy_list(list1)

  if (list2_is_point_pressure_values == 1):
     for item in list2:
        ret.append(float(item[1]))
  else:
    for item in list2:
        ret.append(item)

  return ret

if __name__ == "__main__":
  args = create_args()
  client = udp_client.SimpleUDPClient(args.ip, args.port)

  if(TEST):
    hands_array = np.load(os.getcwd() + "/Testing/hands_rot.npy")
    data = get_mat_data(hands_array)
  else:
     data = get_mat_data()

  print("Welcome to commensalisTECH symBIOsis")
  print("Ctrl+C to exit")
  try:
    while(True):
      if(TEST):
        data = get_mat_data(hands_array)
      else:
         data = get_mat_data()
      values, vector = process_data(data, DATATYPE)
      instructions = compile_instructions(vector, values, DATATYPE)
      print(instructions)
      send_instructions(client, instructions)
      time.sleep(1)
  except KeyboardInterrupt:
    print("\nProgram terminated by user.")