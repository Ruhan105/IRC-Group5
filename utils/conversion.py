import numpy as np


def dist(x, y):
    """Calculate Euclidean distance."""
    return np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)


def find_closest(fire_stations: dict, weather_stations: dict):
    """
    Find the closest weather station to each fire station.

    Takes a dictionary of fire and weather stations 
    in the format {fireID: (x,y), ..}, {weatherID: (x,y), ..}
    Returns a list of each firestation with the closest weather station.
    """
    fire_names = fire_stations.keys
    weather_names = weather_stations.keys
    res = []

    for fire in fire_names:
        min_dist = float("inf")
        current = None
        for weather in weather_names:
            if dist(fire_stations[fire], weather_stations[weather]) < min_dist:
                current = weather
        res.append([fire, current])

    return res
