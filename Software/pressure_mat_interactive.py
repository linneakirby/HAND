from PressureMatPosture import *
import numpy as np

hands_array = np.load("./Testing/hands.npy")
print('hands_array loaded!')

# to save mat data: np.save('./Testing/[filename.npy]', mat.Values)