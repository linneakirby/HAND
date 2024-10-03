import sys
sys.path.append("../")
import datetime

# For mat tests
import unittest
import numpy as np
import os
import matplotlib.pyplot as plt

from pythonosc import udp_client

# My libraries
from Mat import Mat
from Hands import *
import hand_utils
import haptic_assisted_inversions_device as hand
import commensalistech_symbiosis as techbio

class Commensalistech_Symbiosis_Test(unittest.TestCase):

    # @unittest.skip("targeting one test")
    def test_hand_boundaries(self):
        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(hands_array)
        h1_bounds, h2_bounds = h.isolate_hands(hands_array)
        h.generate_cops(h1_bounds, h2_bounds)
        h.find_correction_vector()
        h.select_actuators()

        #print("left hand boundaries: ", h.get_left_hand().get_bounds())
        #print("right hand boundaries: ", h.get_right_hand().get_bounds())

    @unittest.skip("targeting one test")
    #make sure an entire loop runs properly
    def test_simple_sound_trigger(self):
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        testlist = [.9, .2, .2, .4, .6, .9]
        techbio.send_instructions(client, testlist)

    @unittest.skip("targeting one test")
    # make sure two instructions can be carried out in a row
    def test_two_triggers(self):
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        #manually create list
        testlist = list()
        testlist = techbio.add_instruction(testlist, .59)
        testlist = techbio.add_instruction(testlist, .82)
        testlist = techbio.add_instruction(testlist, .19)
        testlist = techbio.add_instruction(testlist, .76)
        testlist = techbio.add_instruction(testlist, .24)
        testlist = techbio.add_instruction(testlist, .94)

        techbio.send_instructions(client, testlist)
        time.sleep(1)

        # should trigger everything?
        testlist2 = [.9, .2, .2, .4, .6, .9]
        techbio.send_instructions(client, testlist2)
    
    @unittest.skip("targeting one test")
    def test_sound_trigger_integrated_actuators(self):  
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        data = techbio.get_mat_data(hands_array)

        actuators, vector = techbio.process_data(data)
        instructions = techbio.compile_instructions(vector, actuators)
        print(instructions)
        time.sleep(1)
        techbio.send_instructions(client, instructions)

    @unittest.skip("targeting one test")
    def test_sound_trigger_integrated_bounds(self):  
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        data = techbio.get_mat_data(hands_array)

        bounds, vector = techbio.process_data(data, 1)
        instructions = techbio.compile_instructions(vector, bounds, True)
        time.sleep(1)
        techbio.send_instructions(client, instructions)

    @unittest.skip("targeting one test")
    def test_sound_trigger_both_bounds(self):  
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        data = techbio.get_mat_data(hands_array)

        # using bounds
        bounds, vector = techbio.process_data(data, 1)
        instructions = techbio.compile_instructions(vector, bounds, True)
        techbio.send_instructions(client, instructions)
        
        time.sleep(1)

        # using actuators
        actuators, vector = techbio.process_data(data)
        instructions = techbio.compile_instructions(vector, actuators)
        techbio.send_instructions(client, instructions)

        time.sleep(1)

    @unittest.skip("targeting one test")
    def test_sound_trigger_integrated_actuators_loop(self):  
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        data = techbio.get_mat_data(hands_array)

        for a in range (5):
            actuators, vector = techbio.process_data(data)
            instructions = techbio.compile_instructions(vector, actuators)
            for i in range (len(instructions)):
                instructions[i] = instructions[i]+a
            print(instructions)
            techbio.send_instructions(client, instructions)
            time.sleep(1)

    # @unittest.skip("targeting one test")
    def test_sound_trigger_integrated_bounds(self):  
        args = techbio.create_args()
        client = udp_client.SimpleUDPClient(args.ip, args.port)

        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        data = techbio.get_mat_data(hands_array)

        for a in range (5):
            bounds, vector = techbio.process_data(data, 1)
            instructions = techbio.compile_instructions(vector, bounds, True)
            for i in range (len(instructions)):
                    instructions[i] = instructions[i]+a
            print(instructions)
            techbio.send_instructions(client, instructions)
            time.sleep(1)


if __name__ == '__main__':
    unittest.main()