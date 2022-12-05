"""The id service, used to assign new objects in the ComosDB database to unique ids

Actions
-------
userid - request a new unique user id
groupid - request a new unique group id
eventid - request a new unique event id"""

import os
import json
import logging

import azure.functions as func
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


ENDPOINT = os.environ.get("ENDPOINT") or ""
KEY = os.environ.get("KEY") or ""


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('groupinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'userid':
        logging.info('    userid request received')
        return func.HttpResponse('Unimplemented', status_code=500)
    elif req_type == 'groupid':
        return func.HttpResponse('Unimplemented', status_code=500)
    elif req_type == 'eventid':
        return func.HttpResponse('Unimplemented', status_code=500)
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)