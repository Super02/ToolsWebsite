import json
from collections import namedtuple

class User:
    def __init__(self, id : str, username : str, password : str, role : str):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
    def __repr__(self):
        return f'<User: {self.username}>'

def createUser(username, password, role):
    return json.dumps(User("oof", username, password, role).__dict__)
def parseUser(data):
    data=json.loads(data)
    return User(data["id"], data["username"], data["password"], data["role"])
def createUserObject(username, password, role):
    return User("oof", username, password, role)