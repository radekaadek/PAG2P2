import pymongo
import json
import geopandas as gpd
from shapely.geometry import mapping

def mongo_init(gj_path, mongo_adr):
    #Reading geojson with data
    gdf = gpd.read_file(gj_path)
    gdf = gdf.to_crs(epsg=4326)
    geojson_data = gdf.to_json()
    geojson_dict = json.loads(geojson_data)

    #Connection to mdb
    connection = pymongo.MongoClient(mongo_adr)
    database = connection.baza
    column = database.stacje
    column.drop()

    #Inserting data to mdb
    column.insert_many(geojson_dict["features"])
    column.create_index([("geometry", "2dsphere")])
    return connection, database, column

def mongo_get_by_polygon(column, poly):
    query = {
        "geometry": {
            "$geoWithin": {
                "$geometry": poly
            }
        }
    }
    features = list(column.find(query))
    return features

if __name__ == '__main__':
    geojson_path = 'Projekt-blok-2/Dane/data.geojson'
    mongo_address = "mongodb://localhost:27017/"
    woj_geojson_path = 'Projekt-blok-2/Dane/woj.geojson'


    woj_gdf = gpd.read_file(woj_geojson_path)
    first_polygon = woj_gdf.iloc[0].geometry
    polygon_gdf = gpd.GeoDataFrame(geometry=[first_polygon], crs="EPSG:4326")
    polygon = mapping(first_polygon)

    con, db, col = mongo_init(geojson_path, mongo_address)
    features_by_polygon = mongo_get_by_polygon(col, polygon)
    con.close()

    print(len(features_by_polygon))
