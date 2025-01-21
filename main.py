import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from file_prep import prep_files
from redis_fun import redis_init
from mongo_fun import mongo_init, mongo_get_by_polygon

#Prep files
# prep_files() #makes geojson from shp (voivodeships, powiats)
#TODO: stats from imgw

#Redis load data and init connection
voivodeships_clean_json = "Projekt-blok-2/Dane/woj.geojson"
powiats_clean_json = "Projekt-blok-2/Dane/powiaty.geojson"
redis_client = redis_init(voivodeships_clean_json, powiats_clean_json) #localhost:6379 hardcoded in redis_fun xd

#Mongo load data and init connection
geojson_path = 'Projekt-blok-2/Dane/data.geojson'
mongo_address = "mongodb://localhost:27017/"
con, col = mongo_init(geojson_path, mongo_address)

#Fast api init
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/voivodeships")
async def get_voivodeships():
    # get voivodeships clean geojsons
    voivodeships_clean = redis_client.hget('voivodeships_clean', 'geojsons')
    if voivodeships_clean is None:
        return HTTPException(status_code=500, detail="Internal server error")
    return json.loads(voivodeships_clean)

@app.get("/powiats")
async def get_powiats():
    # get powiats clean geojsons
    powiats_clean = redis_client.hget('powiaty_clean', 'geojsons')
    if powiats_clean is None:
        return HTTPException(status_code=500, detail="Internal server error")
    return json.loads(powiats_clean)

@app.get("/powiat/{powiat_teryt}")
async def get_powiat(powiat_teryt: str):
    # ask redis for the powiat
    powiat = redis_client.hget('powiaty', powiat_teryt)
    if powiat is not None:
        return powiat
    else:
        return HTTPException(status_code=404, detail="Powiat not found")

@app.get("/voivodeship/{voivodeship_teryt}")
async def get_voivodeship(voivodeship_teryt: str):
    # ask redis for the voivodeship
    voivodeship = redis_client.hget('voivodeships', voivodeship_teryt)
    if voivodeship is not None:
        return voivodeship
    else:
        return HTTPException(status_code=404, detail="Voivodeship not found")

@app.get("/meteo/{voivodeship_teryt}")
async def get_meteo(voivodeship_teryt: str):
    # ask mongo for meteos based on voivodeship
    voivodeship = redis_client.hget('voivodeships', voivodeship_teryt)
    print(voivodeship)
    if voivodeship is None:
        return HTTPException(status_code=404, detail="Voivodeship not found")
    features = mongo_get_by_polygon(col, voivodeship)
    if features is None:
        return HTTPException(status_code=404, detail="Meteo not found")
    return features

redis_client.close()
con.close()
