import pymongo
import json
import geopandas as gpd

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

if __name__ == '__main__':
    geojson_path = 'Projekt-blok-2/Dane/data.geojson'
    mongo_address = "mongodb://localhost:27017/"
    con, db, col = mongo_init(geojson_path, mongo_address)
    con.close()