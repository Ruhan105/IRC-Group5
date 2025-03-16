#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 16:12:19 2025

@author: omarkhan
"""

import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
from scipy.spatial import distance_matrix

# Load fire station locations from CSV
weather_stations = pd.read_csv("all_fire_stations_in_area_fire.csv", skiprows=1)  # Skip the first row if needed

# Extract latitude & longitude from columns [2] & [3]
weather_stations = weather_stations.iloc[:, [2, 3]]
weather_stations.columns = ["Latitude", "Longitude"]  # Rename columns

# Generate synthetic temperature data for these locations
#np.random.seed(42)
weather_stations["Temperature"] = np.random.uniform(50, 110, len(weather_stations))  # Temperature in °F

# Generate midpoints between stations with adjusted temperatures
midpoints = []
temps = []
station_coords = weather_stations[['Latitude', 'Longitude']].values
for i, (lat1, lon1) in enumerate(station_coords):
    for j, (lat2, lon2) in enumerate(station_coords):
        if i < j:  # Only compute each pair once
            mid_lat = (lat1 + lat2) / 2
            mid_lon = (lon1 + lon2) / 2
            temp1 = weather_stations.iloc[i]['Temperature']
            temp2 = weather_stations.iloc[j]['Temperature']
            # Exaggerate midpoints' temps beyond the station temps
            mid_temp = np.mean([temp1, temp2]) + 0.2 * (temp1 - temp2)
            midpoints.append([mid_lat, mid_lon])
            temps.append(mid_temp)

midpoints_df = pd.DataFrame(midpoints, columns=['Latitude', 'Longitude'])
midpoints_df['Temperature'] = temps

# Add ghost points around the borders to smooth the edges
border_expansion = 0.5
border_points = []
border_temps = []
for lat, lon, temp in zip(weather_stations['Latitude'], weather_stations['Longitude'], weather_stations['Temperature']):
    border_points.extend([
        [lat + border_expansion, lon],
        [lat - border_expansion, lon],
        [lat, lon + border_expansion],
        [lat, lon - border_expansion]
    ])
    border_temps.extend([temp] * 4)

border_df = pd.DataFrame(border_points, columns=['Latitude', 'Longitude'])
border_df['Temperature'] = border_temps

# Merge stations, midpoints, and border points for interpolation
interpolation_points = pd.concat([weather_stations, midpoints_df, border_df], ignore_index=True)

# Load California shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = gpd.read_file(url)
california = states[states['name'] == 'California']

# Create interpolation grid
grid_lon, grid_lat = np.meshgrid(
    np.linspace(interpolation_points['Longitude'].min() - border_expansion, interpolation_points['Longitude'].max() + border_expansion, 200),
    np.linspace(interpolation_points['Latitude'].min() - border_expansion, interpolation_points['Latitude'].max() + border_expansion, 200)
)

# RBF interpolation for smoother, distributed heatmap
rbf = Rbf(interpolation_points['Longitude'], interpolation_points['Latitude'], interpolation_points['Temperature'], function='multiquadric', smooth=0.3)
grid_temps_rbf = rbf(grid_lon, grid_lat)

# Convert grid to GeoDataFrame
grid_points = pd.DataFrame({
    'Longitude': grid_lon.ravel(),
    'Latitude': grid_lat.ravel(),
    'Temperature': grid_temps_rbf.ravel()
})
grid_gdf = gpd.GeoDataFrame(grid_points, 
                            geometry=gpd.points_from_xy(grid_points.Longitude, grid_points.Latitude),
                            crs="EPSG:4326")

# Clip heatmap to California borders
clipped_grid = gpd.clip(grid_gdf, california)

# Identify hottest point based on interpolated data
hottest_point = clipped_grid.loc[clipped_grid['Temperature'].idxmax()]

# Plot the map
fig, ax = plt.subplots(figsize=(10, 12))
california.plot(ax=ax, color='lightgrey', edgecolor='black')  # Base map

# Heatmap
sc = ax.scatter(clipped_grid['Longitude'], clipped_grid['Latitude'], c=clipped_grid['Temperature'], 
                cmap='coolwarm', alpha=0.7, s=20)

# Colorbar
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Temperature (°F)')

# Overlay weather stations
ax.scatter(weather_stations['Longitude'], weather_stations['Latitude'], c=weather_stations['Temperature'], 
           cmap='coolwarm', edgecolors='black', s=100, label='Weather Stations')

# Mark the hottest interpolated point
ax.scatter(hottest_point['Longitude'], hottest_point['Latitude'], 
           color='red', edgecolors='black', s=250, marker='x', label='Most Probable Fire Start')

# Add legend
ax.legend(loc='lower left')

# Print hottest point
print(f"Most Probable Fire Start Location: ({hottest_point['Latitude']}, {hottest_point['Longitude']})")
print(f"Temperature: {hottest_point['Temperature']} °F")

plt.show()
