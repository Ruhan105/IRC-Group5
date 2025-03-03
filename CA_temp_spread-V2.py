#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 14:47:02 2025

@author: omarkhan
"""

import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Load fire station locations from CSV
file_path = "all_fire_stations_in_area_fire.csv"  # Ensure this file is in the same directory
fire_stations = pd.read_csv(file_path, skiprows=1)  # Skip the first row if needed

# Extract latitude & longitude from columns [2] & [3]
fire_stations = fire_stations.iloc[:, [2, 3]].dropna()
fire_stations.columns = ["Latitude", "Longitude"]  # Rename columns for clarity

# Generate synthetic temperature data for these locations
np.random.seed(42)
fire_stations["Temperature"] = np.random.uniform(50, 110, len(fire_stations))  # Temperature in °F

# Load California shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(url)
california = states[states['name'] == 'California']

# Create an interpolation grid
grid_lon, grid_lat = np.meshgrid(
    np.linspace(fire_stations['Longitude'].min(), fire_stations['Longitude'].max(), 200),
    np.linspace(fire_stations['Latitude'].min(), fire_stations['Latitude'].max(), 200)
)

# Interpolate temperature data
grid_temps = griddata(
    (fire_stations['Longitude'], fire_stations['Latitude']), fire_stations['Temperature'], 
    (grid_lon, grid_lat), method='cubic'
)

# Convert grid points to a GeoDataFrame
grid_points = pd.DataFrame({
    'Longitude': grid_lon.ravel(), 
    'Latitude': grid_lat.ravel(), 
    'Temperature': grid_temps.ravel()
})
grid_gdf = gpd.GeoDataFrame(grid_points, 
                            geometry=gpd.points_from_xy(grid_points.Longitude, grid_points.Latitude),
                            crs="EPSG:4326")

# Clip the heatmap to California land area
clipped_grid = gpd.clip(grid_gdf, california)

# Plot the map
fig, ax = plt.subplots(figsize=(10, 12))
california.plot(ax=ax, color='lightgrey', edgecolor='black')  # Base map
sc = ax.scatter(clipped_grid.Longitude, clipped_grid.Latitude, c=clipped_grid.Temperature, 
                cmap='coolwarm', alpha=0.6, s=20)

# Colorbar
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Temperature (°F)')

# Title and labels
ax.set_title('Temperature Distribution Over California (Clipped Heatmap)', fontsize=15)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# Overlay scatter points (actual temperature data locations)
ax.scatter(fire_stations['Longitude'], fire_stations['Latitude'], c=fire_stations['Temperature'], 
           cmap='coolwarm', edgecolors='black', s=50, label='Fire Stations')

# Add a legend
ax.legend(loc='lower left')

plt.show()
