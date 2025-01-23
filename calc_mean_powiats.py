import json
from mongo_fun import mongo_get_by_polygon
from pymongo.errors import OperationFailure

def calculate_means_for_powiats(redis_client, col):
    powiats = redis_client.hgetall('powiaty')
    for powiat_id, powiat_data in powiats.items():
        
        try:
            features = mongo_get_by_polygon(col, powiat_data)
        except OperationFailure as e:
            print(f"MongoDB query failed for powiat_id {powiat_id}:")
            continue
        
        if not features:
            continue
        
        means = {}
        count = len(features)
        
        for feature in features:
            for key, value in feature['properties'].items():
                if key.startswith('mean'):
                    if value is None:
                        continue
                    if key not in means:
                        means[key] = 0
                    means[key] += value
        
        for key in means:
            means[key] /= count
        
        for key, value in means.items():
            redis_client.hset(f'powiat_means:{powiat_id}', key, value)