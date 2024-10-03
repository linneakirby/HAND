import sys
sys.path.append("../")
import datetime

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
    
    # @unittest.skip("targeting one test")
    #make sure mat data can be accessed
    def test_load_mat_data(self):
        hands_array = np.load("./hands_rot.npy")
        m = Mat(hands_array)
        self.assertIsInstance(m.Values, np.ndarray)

    # @unittest.skip("targeting one test")
    #make sure there are only 2 clusters
    def test_k_means(self):
        h = Hands()
        hands_array = np.load("./hands_rot.npy")
        h.run_kmeans(hands_array)

        self.assertEqual(len(h.kmeans.cluster_centers_), 2)

    # @unittest.skip("targeting one test")
    #make sure can create a mat data with empty values
    def test_create_mat_zeros(self):
        hands_array = np.zeros(shape=(3,3), dtype=float)
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    # @unittest.skip("targeting one test")
    def test_create_mat_1x3(self):
        hands_array = np.array([1.0, 2.0, 3.0])
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    # @unittest.skip("targeting one test")
    #make sure can create a 2d mat
    def test_create_mat_3x3(self):
        hands_array = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0, 3.0, 3.0]])
        m = Mat(hands_array)

        self.assertIsInstance(m.Values, np.ndarray)

    # @unittest.skip("targeting one test")
    #make sure can find 2 clusters with a simple 2d mat
    def test_kmeans(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0, 0.0]])
        m = Mat(hands_array)
        h = Hands()
        h.run_kmeans(m.Values, 3, 3)

        self.assertEqual(len(h.kmeans.cluster_centers_), 2)

    # @unittest.skip("targeting one test")
    #make sure can find and separate 2 UNORDERED hands with a simple 2d mat
    def test_isolate_hands_unordered(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h.isolate_hands(m.Values)

        #merge hand dictionaries
        rl = dict()
        rl.update(h.h1.get_points())
        rl.update(h.h2.get_points())
    
        self.assertDictEqual(rl, {(2,1): 2.0, (0,1): 1.0})

    # @unittest.skip("targeting one test")
    #make sure can separate and correctly label the hands
    def test_isolate_hands_ordered(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h1_bounds, h2_bounds = h.isolate_hands(m.Values)
        h.generate_cops(h1_bounds, h2_bounds)

        self.assertEqual(h.get_right_hand().get_points().get((2, 1)), 2.0)
        self.assertEqual(h.get_left_hand().get_points().get((0, 1)), 1.0)

    # @unittest.skip("targeting one test")
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

    # @unittest.skip("targeting one test")
    #make sure it's doing all the calculations properly on a simple mat example
    def test_cop_calculations(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0, 0.0]])
        m = Mat(hands_array)
        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h1_bounds, h2_bounds = h.isolate_hands(m.Values)
        h.generate_cops(h1_bounds, h2_bounds)

        self.assertEqual(h.get_right_hand().get_cop(), [2.0, 1.0])
        self.assertEqual(h.get_left_hand().get_cop(), [0.0, 1.0])
        self.assertEqual(h.get_cop(), [4.0/3.0, 1.0])
        self.assertEqual(h.get_ideal_cop(), [1.0, 1.0])

    # @unittest.skip("targeting one test")
    #make sure the basic vector calculation function works
    def test_create_vector(self):
        t1 = [4.0/3.0, 1.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEqual(hand_utils.create_vector(t1, t2), (tv[0], tv[1]))

    # @unittest.skip("targeting one test")
    #make sure the vector is calculated properly using a simple mat example
    def test_vector(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0,0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h1_bounds, h2_bounds = h.isolate_hands(m.Values)
        h.generate_cops(h1_bounds, h2_bounds)
        h.find_correction_vector()
        h.select_actuators()

        t1 = [4.0/3.0, 1.0]
        t2 = [1.0, 1.0]
        tv = [0.0, 0.0]
        tv[0] = t2[0] - t1[0]
        tv[1] = t2[1] - t1[1]

        self.assertEqual(h.get_correction_vector(), (tv[0], tv[1]))

    # @unittest.skip("targeting one test")
    #make sure the actuators are selected properly using a simple mat example
    def test_select_actuators(self):
        hands_array = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0, 0.0, 0.0]])
        m = Mat(hands_array)

        h = Hands()
        h.run_kmeans(m.Values, 3, 3)
        h1_bounds, h2_bounds = h.isolate_hands(m.Values)
        h.generate_cops(h1_bounds, h2_bounds)

        right = h.get_right_hand()
        left = h.get_left_hand()
        #print("right: ", right.get_points())
        #print("left: ", left.get_points())

        h.find_correction_vector()
        #print(f"CoP: {h.cop} - ideal {h.ideal_cop}")
        #print("vector: ", h.get_correction_vector())
        h.select_actuators()

        print("actuators: ", h.actuators)

        self.assertFalse(h.get_actuators().get_r_index().is_on())
        self.assertFalse(h.get_actuators().get_r_right().is_on())
        self.assertFalse(h.get_actuators().get_r_wrist().is_on())
        self.assertFalse(h.get_actuators().get_r_left().is_on())
        self.assertTrue(h.get_actuators().get_l_index().is_on())
        self.assertFalse(h.get_actuators().get_l_right().is_on())
        self.assertTrue(h.get_actuators().get_l_wrist().is_on())
        self.assertFalse(h.get_actuators().get_l_left().is_on())

    # @unittest.skip("targeting one test")
    #make sure an entire loop runs properly
    def test_scatter_plot_integrated(self):
        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        m = Mat(hands_array)
        #tm = np.rot90(m.Values, 2)
        print(m)

        h = Hands()
        h.run_kmeans(hands_array)
        h1_bounds, h2_bounds = h.isolate_hands(hands_array)
        h.generate_cops(h1_bounds, h2_bounds)
        h.find_correction_vector()
        h.select_actuators()

        figure, ax = plt.subplots(figsize=(5,5))
        plt.ion()
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'Results/')
        sample_file_name = results_dir+'test'
        #sample_file_name = results_dir+'correction_'+datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")+'.png'

        hand_utils.generate_scatter_plot(h.kmeans, h.coords_only, h.get_right_hand().get_cop(), h.get_left_hand().get_cop(), h.get_ideal_cop(), h.get_cop(), figure, ax, fp=sample_file_name, p="bw")
        plt.show()

        #print(actuators)

        self.assertFalse(h.get_actuators().get_r_index().is_on())
        self.assertFalse(h.get_actuators().get_r_right().is_on())
        self.assertFalse(h.get_actuators().get_r_wrist().is_on())
        self.assertFalse(h.get_actuators().get_r_left().is_on())
        self.assertTrue(h.get_actuators().get_l_index().is_on())
        self.assertFalse(h.get_actuators().get_l_right().is_on())
        self.assertFalse(h.get_actuators().get_l_wrist().is_on())
        self.assertFalse(h.get_actuators().get_l_left().is_on())

    def test_contour_plot(self):
        hands_array = np.load(os.getcwd() + "/hands_rot.npy")
        m = Mat(hands_array)
        for i in range(3):
            fp='./Results/Sequence/contour'+str(time.time_ns())+'.png'
            m.plotMatrix(fp=fp)


    ### SERVER TESTS BELOW ###
    hands_array = np.load(os.getcwd() + "/hands_rot.npy")
    app, data = hand.create_app(hands_array)

    #create test client
    def setUp(self):
        self.client = self.app.test_client()
    
    @unittest.skip("better to live test")
    def test_server_rhand(self):
        rresponse = self.client.get("/rhand")
        print("r response: ", rresponse.get_data(as_text=True))
        assert rresponse.status_code == 200
        assert "0.0 0.0 0.0 0.0 " == rresponse.get_data(as_text=True)

    @unittest.skip("better to live test")
    def test_server_lhand(self):
        lresponse = self.client.get("/lhand")
        print("l response: ", lresponse.get_data(as_text=True))
        assert lresponse.status_code == 200
        assert "1.0 0.0 0.0 0.0 " == lresponse.get_data(as_text=True)

    @unittest.skip("better to live test")
    def test_server_hand(self):
        response = self.client.get("/hand")
        print("response: ", response.get_data(as_text=True))
        assert response.status_code == 200
        assert "1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 " == response.get_data(as_text=True)

if __name__ == '__main__':
    unittest.main()