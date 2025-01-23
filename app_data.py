from file_prep import prep_files
from data2geojson import download_imgw_data, data2geojson
from redis_fun import redis_init
from mongo_fun import mongo_init
from calc_mean_powiats import calculate_means_for_powiats

# Prep files
# prep_files() #makes geojson from shp (voivodeships, powiats)
# # Imgw
# download_imgw_data()
# data2geojson()

#Redis load data and init connection
voivodeships_clean_json = "Projekt-blok-2/Dane/woj.geojson"
powiats_clean_json = "Projekt-blok-2/Dane/powiaty.geojson"
redis_client = redis_init(voivodeships_clean_json, powiats_clean_json) #localhost:6379 hardcoded in redis_fun xd
if redis_client is None:
    print("Error initializing redis")
    exit(1)


#Mongo load data and init connection
geojson_path = 'Projekt-blok-2/Dane/data.geojson'
mongo_address = "mongodb://localhost:27017/"
con, col = mongo_init(geojson_path, mongo_address)

calculate_means_for_powiats(redis_client, col)

redis_client.close()
con.close()
