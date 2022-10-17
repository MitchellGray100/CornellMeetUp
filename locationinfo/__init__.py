"""The location information microservices. Manages all user location information 
stored in the database

Actions
-------
get - get an existing user's location information
update - update an existing user's location information
add - adds a new user's location information
delete - delete's an existing user's location information"""

import os
import json
import logging

import azure.functions as func
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


ENDPOINT = os.environ.get("ENDPOINT") or ""
KEY = os.environ.get("KEY") or ""
DATABASE_NAME = os.environ.get("DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("CONTAINER_NAME") or ""
PARTITION_KEY = os.environ.get("PARTITION_KEY") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('locationinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'get':
        logging.info('    get request received')
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            user_object = await container.read_item(item=f'location/{username}',partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            res_object = {'latitude': user_object['latitude'], 'longitude': user_object['logitude']}
            return func.HttpResponse(json.dumps(res_object), status_code=200)

    elif req_type == 'update':
        logging.info('    update request received')
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            user_object = await container.read_item(item=f'location/{username}',partition_key=PARTITION_KEY)
            body: dict[str,str] = req.get_json()
            user_object['latitude'] = body['latitude']
            user_object['logitude'] = body['logitude']
            await container.replace_item(item=f'location/{username}',body=user_object)
        except ValueError:
            return func.HttpResponse('Request malformed: body not json', status_code=400)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)

    elif req_type == 'add':
        logging.info('    add request received')
        try:
            body: dict[str,str] = req.get_json()
            await container.create_item(body)
        except ValueError:
            return func.HttpResponse('Request malformed: body not json', status_code=400)
        except CosmosHttpResponseError:
            return func.HttpResponse('User already exists', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)
        
    elif req_type == 'delete':
        logging.info('    delete request received')
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            await container.delete_item(item=f'location/{username}', partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)
    
    else:
        logging.warn('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
