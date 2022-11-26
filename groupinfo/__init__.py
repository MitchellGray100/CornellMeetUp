"""The group information microservices. Manages all group information 
stored in the database

Actions
-------
getmembers - get an existing group's list of members
getevents - get an existing group's list of events
addmember - add a user to an existing group
addevent - add an event to an existing group
removemember - remove an existing user from an existing group
removeevent - remove an existing event from an existing group
newgroup - create a new group

Group Data Object
--------------------
groupname: str - name of group (UNIQUE)
members: list[str] - list of usernames of users in group
events: list[str] - list of ids of events local to this group"""

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
DATABASE_NAME = os.environ.get("DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("CONTAINER_NAME") or ""
PARTITION_KEY = os.environ.get("PARTITION_KEY") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('groupinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'getmembers':
        logging.info('    getmembers request received')
        groupname = req.params.get('groupname')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            res_object = {'members': group_object['members']}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(res_object), status_code=200)

    elif req_type == 'getevents':
        logging.info('    getevents request received')
        groupname = req.params.get('groupname')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            res_object = {'events': group_object['events']}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(res_object), status_code=200)

    elif req_type == 'addmember':
        logging.info('    addmember request received')
        groupname = req.params.get('groupname')
        username = req.params.get('username')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
            members = json.loads(group_object['members'])
            members.append(username)
            group_object['members'] = json.dumps(members)
            await container.replace_item(item=f'groups_{groupname}',body=group_object)
        except ValueError:
            logging.critical('groupinfo internal object store missing members field')
            return func.HttpResponse('Internal server error', status_code=500)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)

    elif req_type == 'addevent':
        logging.info('    addevent request received')
        groupname = req.params.get('groupname')
        eventid = req.params.get('eventid')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif eventid is None:
            logging.error('        request malformed: eventid missing')
            return func.HttpResponse('Request malformed: eventid missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
            members: list = json.loads(group_object['events'])
            members.append(eventid)
            group_object['events'] = json.dumps(members)
            await container.replace_item(item=f'groups_{groupname}',body=group_object)
        except ValueError:
            logging.critical('groupinfo internal object store missing events field')
            return func.HttpResponse('Internal server error', status_code=500)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)
        
    elif req_type == 'removemember':
        logging.info('    removemember request received')
        groupname = req.params.get('groupname')
        username = req.params.get('username')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif username is None:
            logging.error('        request malformed: username missing')
            return func.HttpResponse('Request malformed: username missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
            members: list = json.loads(group_object['members'])
            members.remove(username)
            group_object['members'] = json.dumps(members)
            await container.replace_item(item=f'groups_{groupname}',body=group_object)
        except ValueError:
            logging.warn('        member already exists')
            return func.HttpResponse('Member already removed', status_code=400)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)

    elif req_type == 'removeevent':
        logging.info('    removeevent request received')
        groupname = req.params.get('groupname')
        eventid = req.params.get('eventid')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        elif eventid is None:
            logging.error('        request malformed: eventid missing')
            return func.HttpResponse('Request malformed: eventid missing', status_code=400)
        try:
            group_object = await container.read_item(item=f'groups_{groupname}',partition_key=PARTITION_KEY)
            events: list = json.loads(group_object['events'])
            events.remove(eventid)
            group_object['events'] = json.dumps(events)
            await container.replace_item(item=f'groups_{groupname}',body=group_object)
        except ValueError:
            logging.warn('        event already removed')
            return func.HttpResponse('Event already removed', status_code=400)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)

    elif req_type == 'newgroup':
        logging.info('    newgroup request received')
        try:
            groupname = req.params.get('groupname')
            if groupname is None:
                logging.error('        request malformed: groupname missing')
                return func.HttpResponse('Request malformed: groupname missing', status_code=400)
            group_object = {'groupname': f'groups_{groupname}', 'members': '[]', 'events': '[]'}
            await container.create_item(group_object)
        except CosmosHttpResponseError:
            logging.warn('        user already exists')
            return func.HttpResponse('User already exists', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200)
    
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
