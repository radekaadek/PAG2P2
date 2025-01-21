import json
import redis

def redis_init(voivodeships_path, powiats_path):
    # load geojsons back as python jsons
    voivodeships_clean_json = json.load(open(voivodeships_path))
    powiats_clean_json = json.load(open(powiats_path))


    # Example: Storing data in Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.flushdb()

    # add voivodeships and powiats to redis
    for voivodeship in voivodeships_clean_json['features']:
        redis_client.hset('voivodeships', voivodeship['properties']['national_c'], json.dumps(voivodeship))
    for powiat in powiats_clean_json['features']:
        redis_client.hset('powiaty', powiat['properties']['national_c'], json.dumps(powiat))
    # add clean voivodeships and powiats
    redis_client.hset('voivodeships_clean', 'geojsons', json.dumps(voivodeships_clean_json))
    redis_client.hset('powiaty_clean', 'geojsons', json.dumps(powiats_clean_json))
    return redis_client

if __name__ == '__main__':
    voivodeships_clean_json = "Projekt-blok-2/Dane/woj.geojson"
    powiats_clean_json = "Projekt-blok-2/Dane/powiaty.geojson"
    redis_c = redis_init(voivodeships_clean_json, powiats_clean_json)
