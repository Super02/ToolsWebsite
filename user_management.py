import json
from collections import namedtuple
from firebaseUtil import get_fb_instance
import pyrebase
from json import JSONDecodeError


class User:
    def __init__(self, id: str, username: str, password: str, role: int, email : str):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.email = email

    def __repr__(self):
        return f'<User: {self.username}>'

def createUser(username, password, role, email, *id):
    return createUserObject(username, password, role, email, *id).__dict__
def parseUser(data): # Smarter implementation
    if(isinstance(data, str)):
        data=json.loads(data)
        return User(data["id"], data["username"], data["password"], data["role"], data["email"])
    elif(str(type(data) == "<class 'pyrebase.pyrebase.Pyre'>")):
        return parseUser(data.val())
    else:
        raise(TypeError(str(type(data)) + " was given expected type JSON or PyreBase"))
def createUserObject(username, password, role, email, *id):
    ID=0
    if(getUsers() != None): ID=len(getUsers())
    if(len(id) == 0):
        return User(ID, username, password, role, email)
    else:
        return User(id[0], username, password, role, email)
def getUsers():
    return get_fb_instance().child("users").get().each()
