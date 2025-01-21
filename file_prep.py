import geopandas as gpd

def prep_files() -> None:
    # Load voivodeship and powiat data
    voivodeships = gpd.read_file("Projekt-blok-2/Dane/woj.shp")
    powiats = gpd.read_file("Projekt-blok-2/Dane/powiaty.shp")
    # drop all columns except national_c - TERYT
    voivodeships_clean = voivodeships[['national_c', 'geometry']]
    powiats_clean = powiats[['national_c', 'geometry']]
    # reproject to WGS84
    voivodeships_clean = voivodeships_clean.to_crs(epsg=4326)
    powiats_clean = powiats_clean.to_crs(epsg=4326)
    voivodeships_clean.to_file("Projekt-blok-2/Dane/woj.geojson", driver="GeoJSON")
    powiats_clean.to_file("Projekt-blok-2/Dane/powiaty.geojson", driver="GeoJSON")

if __name__ == '__main__':
    prep_files()