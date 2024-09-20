import argparse
import time

from pythonosc import udp_client


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

if __name__ == "__main__":
  args = create_args()
  client = udp_client.SimpleUDPClient(args.ip, args.port)


  send_instruction(client, 0.1)
  time.sleep(1)
  send_instruction(client, 0.5)
  time.sleep(1)
  send_instruction(client, 0.8)