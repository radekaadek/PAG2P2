import pandas as pd
import geopandas as gpd
import requests, zipfile, io
import os

def download_imgw_data(output_directory = r"Projekt-blok-2\data_meteo"):
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
    valid_urls = ["https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-01.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-02.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-03.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-04.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-05.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-06.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-07.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-08.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-09.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-10.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-11.zip",
    "https://danepubliczne.imgw.pl/datastore/getfiledown/Arch/Telemetria/Meteo/2024/Meteo_2024-12.zip"]

    # Uncomment the line below to use the fetch function if a valid URL is available
    for url in valid_urls:
        print('Downloading data from:', url)
        fetch_and_extract_data(url, output_directory)

def data2geojson(baza = r'Projekt-blok-2\dane\effacility.geojson', output_directory = r"Projekt-blok-2\data_meteo", save_path = r'Projekt-blok-2\dane\data.geojson'):
    mean_tab = []
    for file in os.listdir(output_directory):
        if file.endswith(".csv") and file.startswith("B00300S_2024"):
            try:
                air_temp = pd.read_csv(os.path.join(output_directory, file), header=None, delimiter=';', decimal=',',
                                       names=['KodSH', 'ParametrSH', 'Data', 'Value'], usecols=[0, 1, 2, 3], dtype={'KodSH': str})
            except ValueError:
                air_temp = pd.read_csv(os.path.join(output_directory, file), header=None, delimiter=';', decimal='.',
                                       names=['KodSH', 'ParametrSH', 'Data', 'Value'], usecols=[0, 1, 2, 3], dtype={'KodSH': str})
            air_temp['Value'] = pd.to_numeric(air_temp['Value'], errors='coerce')
            mean = air_temp.pivot(index='KodSH', columns='Data', values='Value')
            mean_values = mean.mean(axis=1)
            mean_tab.append(mean_values)

    mean_tab = pd.concat(mean_tab, axis=1)
    mean_tab.columns = ['mean1', 'mean2', 'mean3', 'mean4', 'mean5', 'mean6', 'mean7', 'mean8', 'mean9', 'mean10', 'mean11', 'mean12']
    mean_tab.to_csv('Projekt-blok-2/Dane/data_meteo/mean_tab.csv')
    geo_data = gpd.read_file(baza)
    table = gpd.GeoDataFrame(columns=['_id', 'name', 'additional', 'mean1', 'mean2', 'mean3', 'mean4', 'mean5', 'mean6', 'mean7', 'mean8', 'mean9', 'mean10', 'mean11', 'mean12', 'geometry'])

    rows = []
    mean_tab = pd.read_csv('Projekt-blok-2/Dane/data_meteo/mean_tab.csv')
    for kodsh in mean_tab['KodSH'][1:]:
        try:
            geo_row = geo_data[geo_data['ifcid'] == int(kodsh)]
        except ValueError:
            continue
        if not geo_row.empty:
            row = {
                '_id': kodsh,
                'name': geo_row.iloc[0]['name1'],
                'additional': geo_row.iloc[0]['additional'],
                'mean1': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean1'].values[0],
                'mean2': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean2'].values[0],
                'mean3': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean3'].values[0],
                'mean4': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean4'].values[0],
                'mean5': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean5'].values[0],
                'mean6': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean6'].values[0],
                'mean7': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean7'].values[0],
                'mean8': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean8'].values[0],
                'mean9': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean9'].values[0],
                'mean10': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean10'].values[0],
                'mean11': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean11'].values[0],
                'mean12': mean_tab.loc[mean_tab['KodSH'] == kodsh, 'mean12'].values[0],
                'geometry': geo_row.iloc[0]['geometry']
            }
            rows.append(row)

    if rows:
        table = pd.concat([table, gpd.GeoDataFrame(rows)], ignore_index=True)
    table.set_crs(epsg=2180, inplace=True)
    table.to_file(save_path, driver='GeoJSON')
