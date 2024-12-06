import pandas as pd
import geopandas as gpd
from astral import LocationInfo
from astral.sun import sun
import requests, zipfile, io
import datetime
import os
import json
import redis

# Configure location for astronomical calculations
city = LocationInfo("Warsaw", "Poland", "Europe/Warsaw", 52.232222, 21.008333)

# Function to download and extract data
def fetch_and_extract_data(url: str, output_dir: str) -> None:
    """
    Downloads and extracts data from a ZIP file hosted at a given URL.

    Args:
        url (str): URL to the ZIP file.
        output_dir (str): Directory to extract the contents.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            zip_file.extractall(output_dir)
            print(f"Data successfully downloaded and extracted to: {output_dir}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch or extract data: {e}")

# Example: Replace with an actual URL or skip if using local files
valid_url = "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-01.zip"  # Replace with the correct URL
output_directory = "data_meteo"

# Uncomment the line below to use the fetch function if a valid URL is available
# fetch_and_extract_data(valid_url, output_directory)

# Process locally downloaded data if available
data_meteo = None
if os.path.exists(output_directory):
    csv_file = os.path.join(output_directory, "B00300S_2024_01.csv")
    if os.path.isfile(csv_file):
        column_names = ["Station", "ParameterCode", "DateTime", "Temperature"]
        data_meteo = pd.read_csv(csv_file, sep=';', header=None, names=column_names, index_col=False)
        # change , to . in the Temperature column and convert to float
        data_meteo['Temperature'] = data_meteo['Temperature'].str.replace(',', '.')
        data_meteo['Temperature'] = data_meteo['Temperature'].astype(float)
        # convert DateTime column to datetime format
        data_meteo['DateTime'] = pd.to_datetime(data_meteo['DateTime'])
        # print(data_meteo.head())
    else:
        print("CSV file not found in the specified directory.")
else:
    print(f"Directory {output_directory} does not exist. Ensure data is downloaded.")

# Load voivodeship and powiat data
voivodeships = gpd.read_file("Projekt-blok-2/Dane/woj.shp")
powiats = gpd.read_file("Projekt-blok-2/Dane/powiaty.shp")
# save both to geojsons
voivodeships.to_file("Projekt-blok-2/Dane/woj.geojson", driver="GeoJSON")
powiats.to_file("Projekt-blok-2/Dane/powiaty.geojson", driver="GeoJSON")
# load geojsons back as python jsons
voivodeships_json = json.load(open("Projekt-blok-2/Dane/woj.geojson"))
powiats_json = json.load(open("Projekt-blok-2/Dane/powiaty.geojson"))
# print(voivodeships_json)

# Load geospatial data (replace with actual file paths)
geojson_file = "Projekt-blok-2/Dane/effacility.geojson"  # Replace with actual file name
if os.path.isfile(geojson_file):
    gdf_stations = gpd.read_file(geojson_file)
    # print(gdf_stations.head())
else:
    print("GeoJSON file not found. Please verify the file path.")

# Astronomical calculations
def calculate_sun_times(date: datetime.date, location: LocationInfo) -> dict:
    """
    Calculates sun-related times for a given date and location.

    Args:
        date (datetime.date): The date for calculations.
        location (LocationInfo): The location object.

    Returns:
        dict: Sun event times (dawn, sunrise, noon, sunset, dusk).
    """
    s = sun(location.observer, date=date, tzinfo=location.timezone)
    return {
        "dawn": s["dawn"],
        "sunrise": s["sunrise"],
        "noon": s["noon"],
        "sunset": s["sunset"],
        "dusk": s["dusk"]
    }

# Example usage for today's date
today = datetime.date.today()
sun_times = calculate_sun_times(today, city)
# print(f"Sun times for {city.name}: {sun_times}")

# Example: Calculating average temperature (replace 'Temperature' with actual column name)
# Assuming data_meteo contains a column 'Temperature'
if data_meteo is not None and 'Temperature' in data_meteo.columns:
    mean_temperature = data_meteo['Temperature'].mean()
    # print(f"Average temperature: {mean_temperature}")
else:
    # print("Temperature column not found in the data.")
    pass


# Example: Storing data in Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# add voivodeships and powiats to redis
for voivodeship in voivodeships_json['features']:
    redis_client.hset('voivodeships', voivodeship['properties']['gmlid'], json.dumps(voivodeship))

# get voivodeships and powiats from redis
voivodeships_from_redis = redis_client.hgetall('voivodeships')
powiats_from_redis = redis_client.hgetall('powiaty')

print(f"Voivodeships from Redis: {voivodeships_from_redis}")
print(f"Powiats from Redis: {powiats_from_redis}")

# remove all data from redis
redis_client.flushall()


