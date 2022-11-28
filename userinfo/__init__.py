"""The user information microservices. Manages all user information stored in
the database

Actions
-------
get - get an existing user's information
update - update an existing user's information
add - adds a new user's information
delete - deletes a existing user's information

User Data Object
----------------
username: str - username of the user (UNIQUE)
last-online: date - time that the user was last seen
groups: list[int] - a list of group ids
info: dict[str,str] - profile information
    birthday: date - birthday of the user
    time-zone: str - timezone of the user
    profile-picture-id: str - id of profile picture"""

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


def get_user_object(username: str) -> Dict[str,Any]:
    return list(container.query_items(f"SELECT * FROM Container AS C WHERE C.id = 'users_{username}'", enable_cross_partition_query=True))[0]

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('userinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'get':
        logging.info('    get request received')
        username = req.params.get('username')
        if username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            user_object = get_user_object(username)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id users_{username} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(user_object), status_code=200)

    elif req_type == 'update':
        logging.info('    update request received')
        username = req.params.get('username')
        if username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            user_object = get_user_object(username)
            body: dict[str,str] = req.get_json()
            for key in body.keys():
                user_object[key] = body[key]
            container.upsert_item(user_object)
        except ValueError:
            logging.error('        request malformed: body malformed')
            return func.HttpResponse('Request malformed: body malformed', status_code=400)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id users_{username} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)

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
            logging.warn(f'        id users_{body["id"]} already exists')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User already exists', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)
        
    elif req_type == 'delete':
        logging.info('    delete request received')
        username = req.params.get('username')
        if username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            container.delete_item(item=f'users_{username}', partition_key=f'users_{username}')
        except CosmosHttpResponseError as e:
            logging.warn(f'        id users_{username} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)
    
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
