import pymongo
import json
import geopandas as gpd
from pyexpat import features
from shapely.geometry import mapping
import redis

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
    return connection, column

def mongo_get_by_polygon(column, polygon_data):
    feature = json.loads(polygon_data)
    poly = feature['geometry']
    query = {
        "geometry": {
            "$geoWithin": {
                "$geometry": poly
            }
        }
    }
    features = list(column.find(query))
    for feature in features:
        if "_id" in feature:
            feature["_id"] = str(feature["_id"])
    return features

if __name__ == '__main__':
    geojson_path = 'Projekt-blok-2/Dane/data.geojson'
    mongo_address = "mongodb://localhost:27017/"
    woj_geojson_path = 'Projekt-blok-2/Dane/woj.geojson'


    # woj_gdf = gpd.read_file(woj_geojson_path)
    # first_polygon = woj_gdf.iloc[0].geometry
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    polygon_data = redis_client.hget('voivodeships', '04')

    # Initialize MongoDB and query by polygon
    con, col = mongo_init(geojson_path, mongo_address)
    features_by_polygon = mongo_get_by_polygon(col, polygon_data)
    con.close()

    print(features_by_polygon)

