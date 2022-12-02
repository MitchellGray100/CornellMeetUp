"""The chat object consumer service. Populates the database with with new chat messages

Message Object
--------------
groupname: str - name of the group that this message was sent in
author: str - the username of the author of this message
message: str - the contents of the chat message"""

import os
import json
import logging
from typing import List, Dict, Any

import azure.functions as func
import requests

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


ENDPOINT = os.environ.get("COSMOS_ENDPOINT") or ""
KEY = os.environ.get("COSMOS_KEY") or ""
DATABASE_NAME = os.environ.get("USER_DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("USER_CONTAINER_NAME") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


def get_chat_object(groupname: str) -> List[Dict[str,Any]]:
        return list(container.query_items(f"SELECT * FROM Container AS C WHERE C.id = 'chats_{groupname}'", enable_cross_partition_query=True))[0]['chats']

def main(kevents: List[func.KafkaEvent]) -> None:
    logging.info('chatconsumer lambda triggered')

    total = 0
    for kevent in kevents:
        logging.info(f'     processed kevent {kevent.key}')
        message_object: Dict[str,str] = json.loads(kevent.get_body())
        try:
            chat_objects = get_chat_object(message_object['groupname'])
            chat_id = int(chat_objects[-1]['id'])+1
        except:
            chat_objects = []
            chat_id = 1
        chat_objects.append({'id': chat_id, 'author': message_object['author'], 'message': message_object['message']})
        container.upsert_item({'id': f'chats_{message_object["groupname"]}', 'chats': chat_objects})
        total += 1
    
    logging.info(f'chatconsumer finished processing {total} chat messages')
