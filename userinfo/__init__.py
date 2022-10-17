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

import logging

import azure.functions as func
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
