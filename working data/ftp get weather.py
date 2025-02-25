#this is just a backup in case it didnt work in jupyter
import os
import requests

# Base URL
base_url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/"

# List of station IDs (modify as needed)
weatherstn_ids = ["USC00123456", "USC00234567", "USC00345678"]

# Directory to save downloaded files
download_dir = "weather_data"
os.makedirs(download_dir, exist_ok=True)

for station_id in weatherstn_ids:
    file_name = f"{station_id}.csv.gz"  # NOAA files are in .csv.gz format
    file_url = base_url + file_name
    local_file_path = os.path.join(download_dir, file_name)

    # Download the file
    response = requests.get(file_url, stream=True)
    
    if response.status_code == 200:
        with open(local_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded: {file_name}")
    else:
        print(f"Failed to download: {file_name} (Status Code: {response.status_code})")


import os
import requests

# Base URL
base_url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/"

# List of station IDs (modify as needed)
id = ["US1CAAL0022"]

# Directory to save downloaded files
download_dir = "original data"
os.makedirs(download_dir, exist_ok=True)

for station_id in id:
    file_name = f"{station_id}.csv.gz"  # NOAA files are in .csv.gz format
    file_url = base_url + file_name
    local_file_path = os.path.join(download_dir, file_name)

    # Download the file
    response = requests.get(file_url, stream=True)
    
    if response.status_code == 200:
        with open(local_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Downloaded: {file_name}")
    else:
        print(f"Failed to download: {file_name} (Status Code: {response.status_code})")

print(f"Saving to: {local_file_path}")
