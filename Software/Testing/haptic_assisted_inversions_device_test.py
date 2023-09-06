import sys
sys.path.append("../")

# For mat tests
import unittest
import numpy as np
import os
import matplotlib.pyplot as plt

# For server tests
from flask import Flask

# My libraries
from Mat import Mat
from Hands import *
import hand_utils
import haptic_assisted_inversions_device as hand

class Haptic_Assisted_Inversions_Device_Mat_Test(unittest.TestCase):

    #make sure mat data can be accessed
    def test_load_mat_data(self):
        hands_array = np.load("./hands.npy")
        m = Mat(hands_array)
        self.assertIsInstance(m.Values, np.ndarray)

    #make sure there are only 2 clusters
    def test_k_means(self):
        h = Hands()
        hands_array = np.load("./hands.npy")
        h.run_kmeans(hands_array)

        self.assertEqual(len(h.kmeans.cluster_centers_), 2)

    #make sure can create a mat data with empty values
    def test_create_mat_zeros(self):
        hands_array = np.zeros(shape=(3,3), dtype=float)
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    def test_create_mat_1x3(self):
        hands_array = np.array([1.0, 2.0, 3.0])
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    #make sure can create a 2d mat
    def test_create_mat_3x3(self):
        hands_array = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]])
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    #make sure can find 2 clusters with a simple 2d mat
    def test_kmeans(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        m = Mat(hands_array)
        h = Hands()
        h.run_kmeans(m.Values, 3, 3)

        self.assertEqual(len(h.kmeans.cluster_centers_), 2)

    #make sure can find and separate 2 UNORDERED hands with a simple 2d mat
    def test_isolate_hands_unordered(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)

        #merge hand dictionaries
        rl = dict()
        rl.update(h.h1.get_points())
        rl.update(h.h2.get_points())
    
        self.assertDictEqual(rl, {(2,1): 2.0, (0,1): 1.0})

    #make sure can separate and correctly label the hands
    def test_isolate_hands_ordered(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)
        h.generate_cops()

        # for j in range(3-1, -1, -1):
        #     tmp = ""
        #     for i in range(3):
        #         tmp = tmp +   hex(int(m.Values[i][j]))[-1]
        #     print(tmp)
        # print("\n")

        self.assertEqual(h.get_right_hand().get_points().get((2, 1)), 2.0)
        self.assertEqual(h.get_left_hand().get_points().get((0, 1)), 1.0)

    #make sure the basic cop calculation function works
    def test_calculate_cop(self):
        weighted_coords = dict()
        weighted_coords[(2.0, 1.0)] = 2.0
        weighted_coords[(0.0, 1.0)] = 1.0

        unweighted_coords = dict()
        unweighted_coords[(2.0, 1.0)] = 1.0
        unweighted_coords[(0.0, 1.0)] = 1.0

        self.assertEqual(hand_utils.calculate_cop(weighted_coords),[4.0/3.0, 1.0])
        self.assertEqual(hand_utils.calculate_cop(unweighted_coords), [1.0, 1.0])

    #make sure it's doing all the calculations properly on a simple mat example
    def test_cop_calculations(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)
        h.generate_cops()

        self.assertEqual(h.get_right_hand().get_cop(), [2.0, 1.0])
        self.assertEqual(h.get_left_hand().get_cop(), [0.0, 1.0])
        self.assertEqual(h.get_cop(), [4.0/3.0, 1.0])
        self.assertEqual(h.get_ideal_cop(), [1.0, 1.0])

    #make sure the basic vector calculation function works
    def test_create_vector(self):
        t1 = [4.0/3.0, 1.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEqual(hand_utils.create_vector(t1, t2), (tv[0], tv[1]))

    #make sure the vector is calculated properly using a simple mat example
    def test_vector(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0,0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)
        h.generate_cops()
        h.find_correction_vector()
        h.select_actuators()

        t1 = [4.0/3.0, 1.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEqual(h.get_correction_vector(), (tv[0], tv[1]))

    #make sure the actuators are selected properly using a simple mat example
    def test_select_actuators(self):
        hands_array = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)
        h.generate_cops()
        h.find_correction_vector()
        h.select_actuators()

        self.assertTrue(h.get_actuators().get_index().is_on())
        self.assertFalse(h.get_actuators().get_right().is_on())
        self.assertFalse(h.get_actuators().get_wrist().is_on())
        self.assertTrue(h.get_actuators().get_left().is_on())

    #make sure an entire loop runs properly
    def test_scatter_plot_integrated(self):
        hands_array = np.load(os.getcwd() + "/hands.npy")
        m = Mat(hands_array)
        tm = np.rot90(m.Values, 2)

        h = Hands()
        h.run_kmeans(tm)
        h.isolate_hands(tm)
        h.generate_cops()
        h.find_correction_vector()
        h.select_actuators()

        figure, ax = plt.subplots(figsize=(5,5))
        plt.ion()
        hand_utils.generate_scatter_plot(h.kmeans, h.coords_only, h.get_right_hand().get_cop(), h.get_left_hand().get_cop(), h.get_ideal_cop(), h.get_cop(), figure)
        plt.show()

        #print(actuators)

        self.assertTrue(h.actuators.get_index().is_on())
        self.assertFalse(h.actuators.get_right().is_on())
        self.assertFalse(h.actuators.get_wrist().is_on())
        self.assertTrue(h.actuators.get_left().is_on())

    ### SERVER TESTS BELOW ###
    hands_array = np.load(os.getcwd() + "/hands.npy")
    app = hand.create_app(hands_array)

    #create test client
    def setUp(self):
        self.client = self.app.test_client()

    def test_server(self):
        response = self.client.get("/hand")
        assert response.status_code == 200
        assert "Index 0.0\nRight 1.0\nWrist 1.0\nLeft 0.0" == response.get_data(as_text=True)


if __name__ == '__main__':
    unittest.main()