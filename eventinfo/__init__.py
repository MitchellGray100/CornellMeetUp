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
eventname: str - name of the event (UNIQUE)
datetime: date - date and time that the event will occur
latitude: float - latitude of the event's location
longitude: float - longitude of the event's location
description: str - description of event"""

import os
import json
import logging

import azure.functions as func
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from dotenv import load_dotenv
load_dotenv()


ENDPOINT = os.environ.get("ENDPOINT") or ""
KEY = os.environ.get("KEY") or ""


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('eventinfo lambda triggered')

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
