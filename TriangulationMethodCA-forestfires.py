#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 12:42:03 2025

@author: omarkhan
"""
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Load fire station locations from CSV
weather_stations = pd.read_csv("all_fire_stations_in_area_fire.csv", skiprows=1)

# Extract latitude & longitude from columns [2] & [3]
weather_stations = weather_stations.iloc[:, [2, 3]]
weather_stations.columns = ["Latitude", "Longitude"]

# Generate synthetic temperature data for these locations
weather_stations["Temperature"] = np.random.uniform(50, 110, len(weather_stations))

# Convert station coordinates to numpy array
station_coords = weather_stations[['Latitude', 'Longitude']].values

# Perform Delaunay triangulation
tri = Delaunay(station_coords)

# Function to interpolate temperature using barycentric coordinates
def interpolate_temp(A, B, C, T_A, T_B, T_C, P):
    detT = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
    wA = ((B[1] - C[1]) * (P[0] - C[0]) + (C[0] - B[0]) * (P[1] - C[1])) / detT
    wB = ((C[1] - A[1]) * (P[0] - C[0]) + (A[0] - C[0]) * (P[1] - C[1])) / detT
    wC = 1 - wA - wB
    return wA * T_A + wB * T_B + wC * T_C

# Create grid for interpolation
grid_lon, grid_lat = np.meshgrid(
    np.linspace(weather_stations['Longitude'].min(), weather_stations['Longitude'].max(), 200),
    np.linspace(weather_stations['Latitude'].min(), weather_stations['Latitude'].max(), 200)
)

# Interpolate temperature for each grid point
grid_points = []
for i in range(grid_lon.shape[0]):
    for j in range(grid_lon.shape[1]):
        P = [grid_lat[i, j], grid_lon[i, j]]
        simplex = tri.find_simplex(P)
        if simplex != -1:  # Check if the point is inside a triangle
            A, B, C = station_coords[tri.simplices[simplex]]
            T_A = weather_stations.iloc[tri.simplices[simplex][0]]['Temperature']
            T_B = weather_stations.iloc[tri.simplices[simplex][1]]['Temperature']
            T_C = weather_stations.iloc[tri.simplices[simplex][2]]['Temperature']
            temp = interpolate_temp(A, B, C, T_A, T_B, T_C, P)
            grid_points.append([P[1], P[0], temp])

# Convert valid grid points to DataFrame and GeoDataFrame
grid_df = pd.DataFrame(grid_points, columns=['Longitude', 'Latitude', 'Temperature'])
grid_gdf = gpd.GeoDataFrame(grid_df, 
                            geometry=gpd.points_from_xy(grid_df.Longitude, grid_df.Latitude),
                            crs="EPSG:4326")

# Load California shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(url)
california = states[states['name'] == 'California']

# Clip heatmap to California borders
clipped_grid = gpd.clip(grid_gdf, california)

# Plot the map
fig, ax = plt.subplots(figsize=(10, 12))
california.plot(ax=ax, color='lightgrey', edgecolor='black')

# Heatmap
sc = ax.scatter(clipped_grid['Longitude'], clipped_grid['Latitude'], c=clipped_grid['Temperature'], 
                cmap='coolwarm', alpha=0.7, s=20)

# Colorbar
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Temperature (°F)')

# Overlay weather stations
ax.scatter(weather_stations['Longitude'], weather_stations['Latitude'], c=weather_stations['Temperature'], 
           cmap='coolwarm', edgecolors='black', s=100, label='Weather Stations')

# Add legend
ax.legend(loc='lower left')

plt.show()

#%%


import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Load fire station locations from CSV
weather_stations = pd.read_csv("all_fire_stations_in_area_fire.csv", skiprows=1)

# Extract latitude & longitude from columns [2] & [3]
weather_stations = weather_stations.iloc[:, [2, 3]]
weather_stations.columns = ["Latitude", "Longitude"]

# Generate synthetic temperature data for these locations
weather_stations["Temperature"] = np.random.uniform(50, 110, len(weather_stations))

# Convert station coordinates to numpy array
station_coords = weather_stations[['Latitude', 'Longitude']].values

# Perform Delaunay triangulation
tri = Delaunay(station_coords)

# Function to interpolate temperature using barycentric coordinates
def interpolate_temp(A, B, C, T_A, T_B, T_C, P):
    detT = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
    wA = ((B[1] - C[1]) * (P[0] - C[0]) + (C[0] - B[0]) * (P[1] - C[1])) / detT
    wB = ((C[1] - A[1]) * (P[0] - C[0]) + (A[0] - C[0]) * (P[1] - C[1])) / detT
    wC = 1 - wA - wB
    return wA * T_A + wB * T_B + wC * T_C

# Create grid for interpolation
padding = 0.1
lon_min, lon_max = weather_stations['Longitude'].min(), weather_stations['Longitude'].max()
lat_min, lat_max = weather_stations['Latitude'].min(), weather_stations['Latitude'].max()

grid_lon, grid_lat = np.meshgrid(
    np.linspace(lon_min - padding, lon_max + padding, 200),
    np.linspace(lat_min - padding, lat_max + padding, 200)
)

# Interpolate temperature for each grid point
grid_points = []
max_temp = float('-inf')
hottest_point = None
for i in range(grid_lon.shape[0]):
    for j in range(grid_lon.shape[1]):
        P = [grid_lat[i, j], grid_lon[i, j]]
        simplex = tri.find_simplex(P)
        if simplex != -1:  # Inside a triangle
            A, B, C = station_coords[tri.simplices[simplex]]
            T_A = weather_stations.iloc[tri.simplices[simplex][0]]['Temperature']
            T_B = weather_stations.iloc[tri.simplices[simplex][1]]['Temperature']
            T_C = weather_stations.iloc[tri.simplices[simplex][2]]['Temperature']
            temp = interpolate_temp(A, B, C, T_A, T_B, T_C, P)
            if temp > max_temp:
                max_temp = temp
                hottest_point = P
        grid_points.append([P[1], P[0], temp])

# Convert valid grid points to DataFrame and GeoDataFrame
grid_df = pd.DataFrame(grid_points, columns=['Longitude', 'Latitude', 'Temperature'])
grid_gdf = gpd.GeoDataFrame(grid_df, 
                            geometry=gpd.points_from_xy(grid_df.Longitude, grid_df.Latitude),
                            crs="EPSG:4326")

# Load California shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(url)
california = states[states['name'] == 'California']

# Clip heatmap to California borders
clipped_grid = gpd.clip(grid_gdf, california)

# Plot with weather station markings
fig, ax = plt.subplots(figsize=(10, 12))
california.plot(ax=ax, color='lightgrey', edgecolor='black')

sc = ax.scatter(clipped_grid['Longitude'], clipped_grid['Latitude'], c=clipped_grid['Temperature'], 
                cmap='coolwarm', alpha=0.7, s=20)

cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Temperature (°F)')

ax.scatter(weather_stations['Longitude'], weather_stations['Latitude'], c=weather_stations['Temperature'], 
           cmap='coolwarm', edgecolors='black', s=100, label='Weather Stations')

if hottest_point:
    ax.scatter(hottest_point[1], hottest_point[0], color='red', edgecolors='black', s=250, marker='x', label='Most Probable Fire Start')

ax.legend(loc='lower left')
plt.title('Heatmap with Weather Stations')
plt.show()

# Plot without weather station markings
fig, ax = plt.subplots(figsize=(10, 12))
california.plot(ax=ax, color='lightgrey', edgecolor='black')

sc = ax.scatter(clipped_grid['Longitude'], clipped_grid['Latitude'], c=clipped_grid['Temperature'], 
                cmap='coolwarm', alpha=0.7, s=20)

cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Temperature (°F)')

if hottest_point:
    ax.scatter(hottest_point[1], hottest_point[0], color='red', edgecolors='black', s=250, marker='x', label='Most Probable Fire Start')

ax.legend(loc='lower left')
plt.title('Heatmap without Weather Stations')
plt.show()
