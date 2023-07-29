import unittest
import pressure_mat_posture as pmp
import numpy as np

class Pressure_Mat_Posture_Test(unittest.TestCase):

    def test_load_mat_data(self):
        self.assertIsInstance(np.load("./Testing/hands.npy"), np.ndarray)

if __name__ == '__main__':
    unittest.main()