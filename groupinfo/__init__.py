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
id: str - name of group (UNIQUE)
members: list[str] - list of usernames of users in group
events: list[str] - list of ids of events local to this group"""

import os
import json
import logging
from typing import Dict,Any

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


ENDPOINT = os.environ.get("COSMOS_ENDPOINT") or ""
KEY = os.environ.get("COSMOS_KEY") or ""
DATABASE_NAME = os.environ.get("USER_DATABASE_NAME") or ""
CONTAINER_NAME = os.environ.get("USER_CONTAINER_NAME") or ""


client = CosmosClient(ENDPOINT, credential=KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


def get_group_object(groupname: str) -> Dict[str,Any]:
    return list(container.query_items(f"SELECT * FROM c WHERE c.id = 'groups_{groupname}'", enable_cross_partition_query=True))[0]

def main(req: func.HttpRequest) -> func.HttpResponse:
    HEADERS = {'Access-Control-Allow-Origin': "*"}

    logging.info('groupinfo lambda triggered')

    req_type = req.params.get('type')

    if req_type == 'getmembers':
        logging.info('    getmembers request received')
        groupname = req.params.get('groupname')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        try:
            group_object = get_group_object(groupname)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            res_object = {'members': group_object['members']}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(res_object), status_code=200, headers=HEADERS)

    elif req_type == 'getevents':
        logging.info('    getevents request received')
        groupname = req.params.get('groupname')
        if groupname is None:
            logging.error('        request malformed: groupname missing')
            return func.HttpResponse('Request malformed: groupname missing', status_code=400)
        try:
            group_object = group_object = get_group_object(groupname)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            res_object = {'events': group_object['events']}
            logging.info('        request successful')
            return func.HttpResponse(json.dumps(res_object), status_code=200, headers=HEADERS)

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
            group_object = group_object = get_group_object(groupname)
            # members = json.loads(group_object['members'])
            # members.append(username)
            # group_object['members'] = json.dumps(members)
            group_object['members'].append(username)
            container.upsert_item(group_object)
        except ValueError:
            logging.critical('groupinfo internal object store missing members field')
            return func.HttpResponse('Internal server error', status_code=500)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)

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
            group_object = group_object = get_group_object(groupname)
            # members = json.loads(group_object['events'])
            # members.append(eventid)
            # group_object['events'] = json.dumps(members)
            group_object['events'].append(eventid)
            container.upsert_item(group_object)
        except ValueError:
            logging.critical('groupinfo internal object store missing events field')
            return func.HttpResponse('Internal server error', status_code=500)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)
        
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
            group_object = group_object = get_group_object(groupname)
            # members: list = json.loads(group_object['members'])
            # members.remove(username)
            # group_object['members'] = json.dumps(members)
            group_object['members'].remove(username)
            container.upsert_item(group_object)
        except ValueError:
            logging.warn('        member already exists')
            return func.HttpResponse('Member already removed', status_code=400)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)

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
            group_object = group_object = get_group_object(groupname)
            # events: list = json.loads(group_object['events'])
            # events.remove(eventid)
            # group_object['events'] = json.dumps(events)
            group_object['events'].remove(eventid)
            container.upsert_item(group_object)
        except ValueError:
            logging.warn('        event already removed')
            return func.HttpResponse('Event already removed', status_code=400)
        except CosmosHttpResponseError:
            logging.warn('        group does not exist')
            return func.HttpResponse('Group does not exist', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)

    elif req_type == 'newgroup':
        logging.info('    newgroup request received')
        try:
            groupname = req.params.get('groupname')
            if groupname is None:
                logging.error('        request malformed: groupname missing')
                return func.HttpResponse('Request malformed: groupname missing', status_code=400)
            try:
                group_object = get_group_object(groupname)
                logging.warn('        group already exists')
                return func.HttpResponse('Group already exists', status_code=400)
            except:
                pass
            group_object = {'id': f'groups_{groupname}', 'members': [], 'events': []}
            container.upsert_item(group_object)
            container.upsert_item({'id': f'chats_{groupname}', 'chats': []})
        except CosmosHttpResponseError:
            logging.warn('        group already exists')
            return func.HttpResponse('Group already exists', status_code=400)
        else:
            logging.info('        request successful')
            return func.HttpResponse('Okay', status_code=200, headers=HEADERS)
    
    else:
        logging.error('    unknown request received')
        return func.HttpResponse('Request malformed: unknown request type', status_code=400)
