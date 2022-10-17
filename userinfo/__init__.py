"""The user information microservices. Manages all user information stored in
the database

Actions
-------
get - get an existing user's information
update - update an existing user's information
add - adds a new user

User Data Object
----------------
id: int - id of the user
name: str - name/username of the user
last-online: date - time that the user was last seen
groups: list[int] - a list of group ids
info: dict[str,str] - profile information
    birthday: date - birthday of the user
    time-zone: str - timezone of the user
    profile-picture-id: str - id of profile picture"""

from typing import Mapping
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
    logging.info('userinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'get':
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            user_object = await container.read_item(item=username,partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            return func.HttpResponse(json.dumps(user_object), status_code=200)

    elif req_type == 'update':
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        user_object = await container.read_item(item=username,partition_key=PARTITION_KEY)
        try:
            body: dict[str,str] = req.get_json()
            for key in body.keys():
                user_object[key] = body[key]
            container.replace_item(item=username,body=user_object)
        except ValueError:
            return func.HttpResponse('Request malformed: body not json', status_code=400)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)

    elif req_type == 'add':
        try:
            body: dict[str,str] = req.get_json()
            container.create_item(body)
        except ValueError:
            return func.HttpResponse('Request malformed: body not json', status_code=400)
        except CosmosHttpResponseError:
            return func.HttpResponse('User already exists', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)
        
    elif req_type == 'delete':
        username = req.params.get('username')
        if username is None:
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            container.delete_item(username, partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            return func.HttpResponse('Okay', status_code=200)
    
    else:
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
