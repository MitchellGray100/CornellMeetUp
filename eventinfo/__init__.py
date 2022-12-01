"""The event information microservices. Manages all event information stored in
the database

Actions
-------
get - get an existing event's information
update - update an existing event's information
add - adds a new event's information
delete - deletes a existing event's information

Event Data Object
----------------
id: str - name of the event (UNIQUE)
datetime: date - date and time that the event will occur
latitude: float - latitude of the event's location
longitude: float - longitude of the event's location
description: str - description of event"""

import os
import json
import logging
from typing import Dict, Any

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from dotenv import load_dotenv
load_dotenv()


ENDPOINT = os.environ.get("COSMOS_ENDPOINT") or ""
KEY = os.environ.get("COSMOS_KEY") or ""
DATABASE_NAME = os.environ.get("USER_DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("USER_CONTAINER_NAME") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


def get_event_object(eventname: str) -> Dict[str,Any]:
    return list(container.query_items(f"SELECT * FROM c WHERE c.id = 'events_{eventname}'", enable_cross_partition_query=True))[0]

def main(req: func.HttpRequest) -> func.HttpResponse:
    HEADERS = {'Access-Control-Allow-Origin': "*"}

    logging.info('eventinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'get':
        logging.info('    get request received')
        eventname = req.params.get('eventname')
        if eventname is None:
            logging.error('        request malformed: eventname missing')
            return func.HttpResponse('Request malformed: eventname missing', status_code=400)
        try:
            event_object = get_event_object(eventname)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id events_{eventname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('Event does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(event_object), status_code=200, headers=HEADERS)

    elif req_type == 'update':
        logging.info('    update request received')
        eventname = req.params.get('eventname')
        if eventname is None:
            logging.error('        request malformed: eventname missing')
            return func.HttpResponse('Request malformed: eventname missing', status_code=400)
        try:
            event_object = get_event_object(eventname)
            body: dict[str,str] = req.get_json()
            for key in body.keys():
                event_object[key] = body[key]
            container.upsert_item(event_object)
        except ValueError:
            logging.error('        request malformed: body malformed')
            return func.HttpResponse('Request malformed: body malformed', status_code=400)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id events_{eventname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)

    elif req_type == 'add':
        logging.info('    add request received')
        try:
            body: dict[str,str] = req.get_json()
            container.upsert_item(body)
        except ValueError:
            logging.error('        request malformed: body malformed')
            return func.HttpResponse('Request malformed: body malformed', status_code=400)
        except CosmosHttpResponseError as e:
            body: dict[str,str] = req.get_json()
            logging.warn(f'        id eventname_{body["eventname"]} already exists')
            logging.warn(e.exc_msg)
            return func.HttpResponse('Event already exists', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)
        
    elif req_type == 'delete':
        logging.info('    delete request received')
        eventname = req.params.get('eventname')
        if eventname is None:
            logging.error('        request malformed: eventname missing')
            return func.HttpResponse('Request malformed: eventname missing', status_code=400)
        try:
            container.delete_item(item=f'events_{eventname}', partition_key=f'events_{eventname}')
        except CosmosHttpResponseError as e:
            logging.warn(f'        id events_{eventname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)
    
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
