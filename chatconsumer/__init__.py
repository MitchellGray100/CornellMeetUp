"""The chat object consumer service. Populates the database with with new chat messages

Message Object
--------------
groupname: str - name of the group that this message was sent in
author: str - the username of the author of this message
message: str - the contents of the chat message"""

import os
import json
import logging
from typing import List, Dict, Any, Union

import azure.functions as func

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.eventhub import EventHubConsumerClient, PartitionContext, EventData


ENDPOINT = os.environ.get("COSMOS_ENDPOINT") or "https://user-info-login.documents.azure.com:443/"
KEY = os.environ.get("COSMOS_KEY") or "mUWLAyrcFYt70f9VbCTVto21zvaQHUujubLGg9DqCCsUOSdwEsn7Ti2AKhC8EG9o8Ed9l6YCucmNa7udQMpQVA=="
DATABASE_NAME = os.environ.get("USER_DATABASE_NAME") or "Users"
CONTAINER_NAME = os.environ.get("USER_CONTAINER_NAME") or "users-container"

EVENTHUB_CONNECTION = os.environ.get("EventHubsConnectionString") or "Endpoint=sb://cornellmeetup.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=h6AsdpNHSixWhX3cwOO1vpEaZLCmZ/lbahe7XbyWSJA="
EVENTHUB_NAME = os.environ.get("EVENTHUB_NAME") or "chat"


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

consumer = EventHubConsumerClient.from_connection_string(conn_str=EVENTHUB_CONNECTION, consumer_group="$Default",eventhub_name=EVENTHUB_NAME)


def get_chat_object(groupname: str) -> List[Dict[str,Any]]:
    return list(container.query_items(f"SELECT * FROM Container AS C WHERE C.id = 'chats_{groupname}'", enable_cross_partition_query=True))[0]['chats']

def callback(partition_context: PartitionContext, events: List[EventData]) -> None:
    for event in events:
        logging.info(f'     processed kevent {event.message_id}')
        message_object: Dict[str,str] = json.loads(event.body_as_str())
        try:
            chat_objects = get_chat_object(message_object['groupname'])
            chat_id = int(chat_objects[-1]['id'])+1
        except:
            chat_objects = []
            chat_id = 1
        chat_objects.append({'id': chat_id, 'author': message_object['author'], 'message': message_object['message']})
        container.upsert_item({'id': f'chats_{message_object["groupname"]}', 'chats': chat_objects})

def main(mytimer: func.TimerRequest) -> None:
    logging.info('chatconsumer lambda triggered')

    consumer.receive_batch(callback, starting_position="@latest", max_wait_time=3)
    
    logging.info(f'chatconsumer finished processing chat messages')
