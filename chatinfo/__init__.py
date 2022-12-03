"""The chat information microservice. Manages all chat information in the database 
and allows clients to query most recent chats

Actions
-------
getn - get the last N messages from a group's chat
getafter - get all messages after a certain message id from a group's chat
getall - get all messages from a group's chat
send - send a message to a group's chat from a specific user

Chat Data Object
----------------
id: str - the id of the message in the group's chat (UNIQUE)
author: str - the id of the used that authored the message
message: str - the content of the message"""

import os
import json
import logging
from typing import Dict, Any, List

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.eventhub import EventHubProducerClient, EventData


ENDPOINT = os.environ.get("COSMOS_ENDPOINT") or ""
KEY = os.environ.get("COSMOS_KEY") or ""
DATABASE_NAME = os.environ.get("USER_DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("USER_CONTAINER_NAME") or ""

EVENTHUB_CONNECTION = os.environ.get("EventHubsConnectionString") or ""
EVENTHUB_NAME = os.environ.get("EVENTHUB_NAME") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

producer = EventHubProducerClient.from_connection_string(conn_str=EVENTHUB_CONNECTION, eventhub_name=EVENTHUB_NAME)


def get_chat_object(groupname: str) -> List[Dict[str,Any]]:
        return list(container.query_items(f"SELECT * FROM Container AS C WHERE C.id = 'chats_{groupname}'", enable_cross_partition_query=True))[0]['chats']


def main(req: func.HttpRequest) -> func.HttpResponse:
    HEADERS = {'Access-Control-Allow-Origin': "*"}

    logging.info('chatinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'getn':
        logging.info('    getn request received')
        groupname = req.params.get('groupname')
        n = req.params.get('n')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif n is None:
            logging.error('        request malformed: n missing')
            return func.HttpResponse('Request malformed: n missing', status_code=400)
        try:
            chat_object = get_chat_object(groupname)
            n = int(n)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id chats_{groupname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('Chat object does not exist', status_code=400)
        except ValueError:
            logging .error('        request malformed: n is not an integer')
            return func.HttpResponse('Request malformed: n is not an integer', status_code=400)
        else:
            response_object = {'chats': chat_object[-n:]}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(response_object), status_code=200, headers=HEADERS)
    elif req_type == 'getafter':
        logging.info('    getafter request received')
        groupname = req.params.get('groupname')
        chatid = req.params.get('chatid')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif chatid is None:
            logging.error('        request malformed: chatid missing')
            return func.HttpResponse('Request malformed: chatid missing', status_code=400)
        try:
            chat_object = get_chat_object(groupname)
            result = []
            for chat in chat_object[::-1]:
                if chat['id'] == chatid:
                    break
                result.append(chat)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id chats_{groupname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('Chat object does not exist', status_code=400)
        else:
            response_object = {'chats': result}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(response_object), status_code=200, headers=HEADERS)
    elif req_type == 'getall':
        logging.info('    getall request received')
        groupname = req.params.get('groupname')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        try:
            chat_object = get_chat_object(groupname)
        except CosmosHttpResponseError as e:
            logging.warn(f'        id chats_{groupname} does not exist')
            logging.warn(e.exc_msg)
            return func.HttpResponse('Chat object does not exist', status_code=400)
        else:
            response_object = {'chats': chat_object}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(response_object), status_code=200, headers=HEADERS)
    elif req_type == 'send':
        logging.info('    send request received')
        groupname = req.params.get('groupname')
        username = req.params.get('username')
        message = req.get_body().decode()
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        message_object = {'groupname': groupname,'author': username, 'message': message}
        producer.send_event(EventData(json.dumps(message_object)))
        logging.info('        message successfully sent')
        return func.HttpResponse('Okay', status_code=200, headers=HEADERS)
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
