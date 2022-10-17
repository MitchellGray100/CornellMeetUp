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


import json
import os
from flask import Flask, request
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

app = Flask(__name__)


@app.before_first_request
def establish_connection() -> None:
    """Establishes a connection to the CosmosDB database"""
    global client
    pass


@app.route("/get", methods=["GET"])
async def get_user():
    """Gets the user information stored in the database specified by the user id
    Usage: 0.0.0.0/get?username=<username>"""
    username = request.values.get("username")
    if username is None:
        return "ERROR: Request malformed", 400
    user_object = await container.read_item(item=username,partition_key=PARTITION_KEY)
    return json.dumps(user_object), 200


@app.route("/update", methods=["POST"])
async def update_user():
    """Updates the user information stored in the database specified by the username
    and sends back 'OK' if user is found
    Usage: 0.0.0.0/update?username=<username>, body contains fields to update"""
    username = request.values.get("username")
    if username is None:
        return "ERROR: Request malformed", 400
    try :
        user_object = await container.read_item(item=username,partition_key=PARTITION_KEY)
        for key in request.values.keys():
            user_object[key] = request.values[key]
        container.replace_item(item=username,body=user_object)
        return "Okay", 200
    except CosmosHttpResponseError:
        return "ERROR: User not found", 400


@app.route("/add", methods=["POST"])
def add_new_user():
    """Adds new user information to the database and sends back userid of new user
    Usage: 0.0.0.0/add, body contains fields to update"""
    try:
        container.create_item(request.values)
        return "Okay", 200
    except CosmosHttpResponseError:
        return "ERROR: Request malformed", 400

@app.route("/delete", methods=["POST"])
async def delete_user():
    """Deletes the user from the database
    Usage: 0.0.0.0/delete?username=<username>"""
    username = request.values.get("username")
    if username is None:
        return "ERROR: Request malformed", 400
    try:
        container.delete_item(username, partition_key=PARTITION_KEY)
        return "Okay", 200
    except CosmosHttpResponseError:
        return "ERROR: User not found", 400