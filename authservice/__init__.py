"""The authentication microservice. Used to authenticate username/password
combinations.

Actions
-------
register - registers a new user with the given password or changes the password
    for an existing account
authenticate - checks if the username/password combo is correct

Authentication Object
---------------------
username: str - the username of the user
password: str - the hashed and salted password
salt: str - the salt for the user"""

import os
import json
import logging
from typing import Dict,Any
import hashlib
import uuid

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


def get_auth_object(username: str) -> Dict[str,Any]:
    return list(container.query_items(f"SELECT * FROM c WHERE c.id = 'auth_{username}'", enable_cross_partition_query=True))[0]

def main(req: func.HttpRequest) -> func.HttpResponse:
    HEADERS = {'Access-Control-Allow-Origin': "*"}

    logging.info('authservice lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'register':
        logging.info('    register request received')
        username = req.params.get('username')
        password = req.params.get('password')
        if username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        elif password is None:
            logging.error('        request malformed: password missing')
            return func.HttpResponse('Request malformed: password missing', status_code=400)
        try:
            salt = uuid.uuid4().hex
            pass_salt = password + salt
            m = hashlib.sha256()
            m.update(pass_salt.encode())
            hashed_pass = m.hexdigest()
            auth_object = {'id': f'auth_{username}', 'password': hashed_pass, 'salt': salt}
            container.upsert_item(auth_object)
        except CosmosHttpResponseError:
            logging.warn('        error inserting new authentication object')
            return func.HttpResponse('internal error: error inserting new authentication object', status_code=500)
        else:
            logging.info('        password update successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)

    elif req_type == 'authenticate':
        logging.info('    authenticate request received')
        username = req.params.get('username')
        password = req.params.get('password')
        if username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        elif password is None:
            logging.error('        request malformed: password missing')
            return func.HttpResponse('Request malformed: password missing', status_code=400)
        try:
            auth_object = get_auth_object(username)
        except CosmosHttpResponseError:
            logging.warn('        user does not exist')
            return func.HttpResponse('User does not exist', status_code=400)
        else:
            salt: str = auth_object['salt']
            pass_salt = password + salt
            m = hashlib.sha256()
            m.update(pass_salt.encode())
            hashed_pass = m.hexdigest()
            if hashed_pass == auth_object['password']:
                logging.info('        authentication successful')
                return func.HttpResponse('true', status_code=200, headers=HEADERS)
            else:
                logging.info('        authentication not successful')
                return func.HttpResponse('false', status_code=200, headers=HEADERS)
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
