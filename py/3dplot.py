import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Read data from text file
data = np.loadtxt('points_xyz_positions.txt', skiprows=1)

# Extract columns
x_points = data[:, 1]
y_points = data[:, 2]
z_points = data[:, 3]


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_points, y_points, z_points, c='r', marker='o')

# Label points
for i, (x, y, z) in enumerate(zip(x_points, y_points, z_points)):
    ax.text(x, y, z, str(i), color='blue')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
