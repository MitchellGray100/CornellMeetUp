"""The route calculation service. Calculates the closest location between multiple
origins to find the best meeting location between groups of users."""

import os
import json
import logging
import math
from typing import List, Dict, Union, Any

import azure.functions as func
import requests
import numpy as np

MAPS_SUBSCRIPTION_KEY = os.environ.get("MAPS_SUBSCRIPTION_KEY") or ""


def calculate_distances(origins: List[List[float]], destination: List[float]) -> Union[List[int], None]:
    message_body = {
        "origins": {
            "type": "MultiPoint",
            "coordinates": origins
        },
        "destinations": {
            "type": "MultiPoint",
            "coordinates": [destination]
        }
    }

    r = requests.post(
            f"https://atlas.microsoft.com/route/matrix/sync/json?api-version=1.0&subscription-key={MAPS_SUBSCRIPTION_KEY}&routeType=shortest",
            json=json.dumps(message_body)
        )
    if not r.ok:
        return None
    
    result: List[int] = []
    matrix: List[Dict[str,Any]] = r.json()['matrix']
    for element in matrix:
        if element['statusCode'] != 200:
            return None
        result.append(element['response']['routeSummary']['lengthInMeters'])
    return result

def get_error(distances: List[int]) -> float:
    return (max(distances) - min(distances)) / max(distances)

def get_centroid(points: List[List[float]]) -> List[float]:
    sumx = sum(p[0] for p in points)
    sumy = sum(p[1] for p in points)
    return [sumx / len(points), sumy / len(points)]

def calculate_new_destination(origins: List[List[float]], destination: List[float], distances: List[int]) -> List[float]:
    maxorigin_vec = np.array(origins[distances.index(min(distances))])
    minorigin_vec = np.array(origins[distances.index(min(distances))])
    destination_vec = np.array(destination)
    norm_vec = (maxorigin_vec - destination_vec) / np.linalg.norm(maxorigin_vec - destination_vec)
    length = (np.linalg.norm(maxorigin_vec) - np.linalg.norm(minorigin_vec)) / 2
    move_vec = norm_vec*length
    return (destination_vec + move_vec).tolist()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('routeservice lambda triggered')

    try:
        body = json.loads(req.get_json())
        origins: List[List[float]] = body['origins']
    except:
        logging.error('        request malformed: body malformed')
        return func.HttpResponse('Request malformed: body malformed', status_code=400)
    else:
        destination = get_centroid(origins)
        distances = calculate_distances(origins,destination)
        if distances is None:
            logging.error('        internal error: Azure Maps API response error')
            return func.HttpResponse('Internal error: Azure Maps API response error', status_code=500)
        error = get_error(distances)
        while error > 0.1:
            destination = calculate_new_destination(origins,destination,distances)
            distances = calculate_distances(origins,destination)
            if distances is None:
                logging.error('        internal error: Azure Maps API response error')
                return func.HttpResponse('Internal error: Azure Maps API response error', status_code=500)
            error = get_error(distances)
            
        
        result_object = {'destination': destination}
        return func.HttpResponse(json.dumps(result_object), status_code=200)
