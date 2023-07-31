import unittest
import pressure_mat_posture as pmp
import numpy as np

class Pressure_Mat_Posture_Test(unittest.TestCase):

    #make sure mat data can be accessed
    def test_load_mat_data(self):
        self.assertIsInstance(np.load("./Testing/hands.npy"), np.ndarray)

    #make sure there are only 2 clusters
    def test_k_means(self):
        hands_array = np.load("./Testing/hands.npy")
        kmeans, coords_only = pmp.run_kmeans(hands_array)

        self.assertEquals(len(kmeans.cluster_centers_), 2)

    #make sure can create a mat data with empty values
    def test_create_mat_zeros(self):
        m = np.zeros(shape=(3,3), dtype=float)

        self.assertIsInstance(m, np.ndarray)

    def test_create_mat_1x3(self):
        m = np.array([1.0, 2.0, 3.0])

        self.assertIsInstance(m, np.ndarray)

    #make sure can create a 2d mat
    def test_create_mat_3x3(self):
        m = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0], [3.0,3.0,3.0]])

        self.assertIsInstance(m, np.ndarray)

    #make sure can find 2 clusters with a simple 2d mat
    def test_kmeans(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 1.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)

        self.assertEquals(len(kmeans.cluster_centers_), 2)

    #make sure can find and separate 2 hands with a simple 2d mat
    def test_isolate_hands(self):
        m = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [0.0,0.0,0.0]])
        kmeans, coords_only = pmp.run_kmeans(m, 2, 3, 3)
        r, l = pmp.isolate_hands(m, kmeans, coords_only)

        #merge hand dictionaries
        rl = dict()
        rl.update(r)
        rl.update(l)
    
        self.assertDictEqual(rl, {(1,2): 2.0, (1,0): 1.0})

if __name__ == '__main__':
    unittest.main()