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
profile: str - profile information (bio, blurb, given info)
groups: list[int] - a list of group ids"""

import json
from flask import Flask, request

app = Flask(__name__)

@app.route("/get", methods=["GET"])
def get_user():
    """Gets the user information stored in the database specified by the user id
    Usage: 0.0.0.0/get?userid=<userid>"""
    userid = request.args.get("userid")
    # Get user data object from db
    # Deserialize user data object
    # Convert data object to message body
    return userid or ""

@app.route("/update", methods=["POST"])
def update_user():
    """Updates the user information stored in the database specified by the user id
    and sends back 'OK' if user is found
    Usage: 0.0.0.0/update?userid=<userid>, body contains fields to update"""
    userid = request.args.get("userid")
    # Check if user exists
    # Get user data object from db
    # Deserialize data object
    # Modify user data object
    # Serialize user data object
    # Push new user object to db
    return userid or ""


@app.route("/add", methods=["POST"])
def add_new_user():
    """Adds new user information to the database and sends back userid of new user
    Usage: 0.0.0.0/add, body contains fields to update"""
    # Convert message body to user object
    # Serialize user data object
    # Push new user object to db
    return ""


def serialize_user(user: dict[str,str]) -> bytes:
    """Serializes the user data object to the form it is stored as in the database"""
    return json.dumps(user).encode()


def deserialize_user(bytestring: bytes) -> dict[str,str]:
    """Deserializes the user data object to the form it is stored as in the database"""
    return json.loads(bytestring.decode())
