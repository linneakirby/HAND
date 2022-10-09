from tqdm import tqdm
from pressure_mat_posture import *
import numpy as np

# Sensor rows + columns
ROWS = 48 
COLS = 48


hands_array = np.load("./Testing/hands.npy")
print('hands_array loaded!')

# Heat map of pressure points
# aka fire hands
plt.imshow(hands_array, cmap='hot', interpolation='nearest')
plt.show()

kmeans = KMeans(n_clusters=2)

# Creates a new array with the coordinates only of each point with a nonzero
# reading from the pressure mat
# 
# Basically, to force kmeans to only consider the coordinates
# of the points--not the sensor reading--when clustering.
coords_only = []
index = 0

for row in range(ROWS):
    for col in range(COLS):
        if hands_array[row][col]!=0:
            coords_only.append([row, col])
        index+=1


kmeans.fit(coords_only)

# I was tired of graphing so here is the worst possible visualization for this data
index = 0
for row in range(ROWS):
    for col in range(COLS):
        if [row, col] in coords_only:
            if kmeans.labels_[index] == 1:
                print('X', end="")
            if kmeans.labels_[index] == 0:
                print('o', end="")
            index+=1
        else:
            print("-", end="")
    print()