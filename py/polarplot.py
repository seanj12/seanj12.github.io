# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 13:29:11 2024

@author: shalpin-jordan
"""

import csv
import matplotlib.pyplot as plt
import numpy as np

def create_polar_plot(filename, row_number):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for _ in range(row_number-1):  # Skip rows until the desired row
            next(reader)
        row = next(reader)  # Read desired row
        elevation = float(row[0])  # Elevation value from the row
        azimuth = float(row[1])    # Azimuth value from the row
        channels = list(map(float, row[2:45]))  # Convert channel values to floats

    # Define angles for the channels
    num_channels = len(channels)
    angles = np.linspace(0, 2*np.pi, num_channels, endpoint=False)

    # Plotting
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(angles, channels, marker='o', linestyle='-', label='Channel Values')

    # Add channel values as labels around the plot
    ax.set_xticks(angles)
    ax.set_xticklabels(range(43))

    # Add title with azimuth and elevation values
    ax.set_title(f'Polar Plot of Channel Values\nAzimuth: {azimuth}, Elevation: {elevation}')


    # Move the legend outside the plot
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    # Set the direction of the zero angle to be at the top (North)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)  # Reverse direction for theta

    plt.show()

# Assuming your CSV file is named "data.csv"
filename = "data-2024-04-22 17-25-57.csv"
row_number = 436 #Row in excel to plot
create_polar_plot(filename, row_number)
