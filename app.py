import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from redis_fun import redis_con
from mongo_fun import mongo_con, mongo_get_by_polygon

# Connection to redis
redis_client = redis_con()

#Mongo load data and init connection
mongo_address = "mongodb://localhost:27017/"
con, col = mongo_con(mongo_address)

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
    if voivodeship is None:
        return HTTPException(status_code=404, detail="Voivodeship not found")
    features = mongo_get_by_polygon(col, voivodeship)
    if features is None:
        return HTTPException(status_code=404, detail="Meteo not found")
    return features

@app.get("/powiat_meteo/{powiat_teryt}")
async def get_powiat_means(powiat_teryt: str):
    print(f"powiat_means: b'{powiat_teryt}'")
    means = redis_client.hgetall(f"powiat_means:b'{powiat_teryt}'")
    if not means:
        return HTTPException(status_code=404, detail="Powiat means not found")
    return {key.decode('utf-8'): float(value) for key, value in means.items()}

@app.get("/powiats_in_voivodeship/{voivodeship_teryt}")
async def get_powiats_in_voivodeship(voivodeship_teryt: str):
    powiats = redis_client.hgetall('powiaty')
    matching_powiats = [json.loads(value) for key, value in powiats.items() if key.decode('utf-8').startswith(f"{voivodeship_teryt}")]
    if not matching_powiats:
        return HTTPException(status_code=404, detail="No powiats found for the given voivodeship")
    return matching_powiats