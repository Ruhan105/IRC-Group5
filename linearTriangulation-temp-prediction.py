#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 17:43:44 2025

@author: omarkhan
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from matplotlib.tri import Triangulation

# Load fire station locations from CSV
weather_stations = pd.read_csv("all_fire_stations_in_area_fire.csv", skiprows=1)

# Extract latitude & longitude from columns [2] & [3]
weather_stations = weather_stations.iloc[:, [2, 3]]
weather_stations.columns = ["Latitude", "Longitude"]

# Generate synthetic temperature data for these locations
weather_stations["Temperature"] = np.random.uniform(50, 110, len(weather_stations))

# Convert station coordinates to numpy array
station_coords = weather_stations[['Longitude', 'Latitude']].values  # Matplotlib uses (x, y) -> (lon, lat)

# Perform Delaunay triangulation
tri = Delaunay(station_coords)

# Extract triangle vertex indices
triangles = tri.simplices

# Compute average temperature for each triangle
triangle_temps = np.array([
    weather_stations.iloc[triangles[i]].Temperature.mean() for i in range(len(triangles))
])

# Load California shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(url)
california = states[states['name'] == 'California']

# Find the hottest point within the triangulated area
max_temp_idx = np.argmax(triangle_temps)
hottest_triangle = triangles[max_temp_idx]
hottest_point = station_coords[hottest_triangle].mean(axis=0)  # Approximate fire start as triangle centroid

# Plot the map
fig, ax = plt.subplots(figsize=(10, 12))

# Plot California state border with more vivid edges
california.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1.5)

# Create triangulation object
triang = Triangulation(station_coords[:, 0], station_coords[:, 1], triangles)

# Plot triangulated temperature map without black lines between triangles
tpc = ax.tripcolor(triang, triangle_temps, cmap='coolwarm')

# Add colorbar
cbar = plt.colorbar(tpc, ax=ax)
cbar.set_label('Temperature (°F)')

# Overlay weather stations
ax.scatter(weather_stations['Longitude'], weather_stations['Latitude'], c=weather_stations['Temperature'], 
           cmap='coolwarm', edgecolors='black', s=50, label='Weather Stations')

# Plot the estimated fire start location
ax.scatter(hottest_point[0], hottest_point[1], color='red', edgecolors='black', s=300, marker='P', label='Most Probable Fire Start')

# Add legend
ax.legend(loc='lower left')
plt.title('Triangulated Temperature Map (No Interior Interpolation, No Triangle Edges)')

plt.show()
