"""Test microservice, used for testing only. Not for production"""

import os
import json
import logging

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


def main(req: func.HttpRequest) -> func.HttpResponse:
    # result = ''
    # for dict in container.read_all_items():
    #     result += str(dict) + "\n"
    # result = container.read()
    result = f'{ENDPOINT}\n{KEY}\n{DATABASE_NAME}\n{CONTAINER_NAME}\n'
    return func.HttpResponse(str(result), status_code=200)
