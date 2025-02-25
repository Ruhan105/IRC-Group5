import pandas as pd
from geopy.distance import geodesic

# Load fire stations and weather stations data
fire_stations = pd.read_csv("working data\all fire stations in area_ fire.csv")  # Fire stations CSV
weather_stations = pd.read_csv("working data\ghcnd-stations.csv")  # Weather stations CSV

# Ensure the columns match: fire stations (id, name, lat, lon), weather stations (id, name, lat, lon)
fire_stations = fire_stations.rename(columns={"latitude": "lat", "longitude": "lon"})
weather_stations = weather_stations.rename(columns={"latitude": "lat", "longitude": "lon"})

# Function to find the closest weather station
def find_closest_weather_station(fire_station):
    fire_coords = (fire_station["lat"], fire_station["lon"])
    closest_station = None
    min_distance = float("inf")
    
    for _, weather_station in weather_stations.iterrows():
        weather_coords = (weather_station["lat"], weather_station["lon"])
        distance = geodesic(fire_coords, weather_coords).km  # Calculate distance in km
        
        if distance < min_distance:
            min_distance = distance
            closest_station = weather_station["id"]
    
    return closest_station

# Apply function to each fire station
fire_stations["closest_weather_station"] = fire_stations.apply(find_closest_weather_station, axis=1)

# Save the results
fire_stations.to_csv("matched_fire_weather_stations.csv", index=False)

print("✅ Matching complete! Results saved to 'matched_fire_weather_stations.csv'.")
