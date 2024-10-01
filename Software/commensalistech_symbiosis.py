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
CONTOUR = False




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

def process_mat_data(d):
    h = Hands()
    if np.any(d):
        h.run_kmeans(d)
        h.isolate_hands(d)
        h.generate_cops()
        h.find_correction_vector()
        print(f"CoP: {h.cop} - ideal {h.ideal_cop}")
        h.select_actuators()
    return h.get_actuators(), h.get_cop()

def process_data_helper(data):
    #if data is just mat values snapshot
    # used for testing without Mat object
    if isinstance(data, np.ndarray):
      return process_mat_data(data)
    #if data is a Mat object -> used for normal HAND behavior
    if isinstance(data, Mat):
      data.get_matrix()
      #print(data)
      a, c = process_mat_data(data.Values)
      if CONTOUR:
          data.plotMatrix()
      return a, c

# process both hands
def process_data(data):
  a, c = process_data_helper(data)
  return a.get_actuator_list_2(), c

def get_mat_data(data = None):
  if data is None: #if no mat values provided
      data = Mat(hand_utils.get_port())
  return data

def compile_instructions(list1, list2):
  ret = copy_list(list1)

  for item in list2:
      ret.append(item)

  return ret

if __name__ == "__main__":
  args = create_args()
  client = udp_client.SimpleUDPClient(args.ip, args.port)

  hands_array = np.load(os.getcwd() + "/Testing/hands_rot.npy")
  data = get_mat_data(hands_array)
  a, c = process_data(data)
  instructions = compile_instructions(c, a)
  print(instructions)
  send_instructions(client, instructions)