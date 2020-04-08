import json
from collections import namedtuple
from firebaseUtil import get_fb_instance
import pyrebase
from json import JSONDecodeError
import time, base64


class User:
    def __init__(
            self,
            id: str,
            username: str,
            password: str,
            role: int,
            email: str,
            notes: str):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.email = email
        self.notes = notes

    def __repr__(self):
        return f'<User: {self.username}>'


def createUser(username, password, role, email, *id):
    return createUserObject(username, password, role, email, *id).__dict__


def parseUser(data):  # Smarter implementation
    if(isinstance(data, str)):
        data = json.loads(data)
        return User(
            data["id"],
            data["username"],
            data["password"],
            data["role"],
            data["email"],
            data["notes"])
    elif(isinstance(data, User)):
        return data
    elif(str(type(data)) == "<class 'pyrebase.pyrebase.Pyre'>"):
        try:
            return parseUser(data.val())
        except AttributeError as e:
            print(str(e) + " at line 32 in user_management")
    else:
        raise(TypeError(str(type(data)) +
                        " was given expected type JSON or PyreBase"))


def createUserObject(username, password, role, email, *id):
    ID = createID()
    if(len(id) == 0):
        return User(ID, username, password, role, email, "")
    else:
        return User(id[0], username, password, role, email, "")


def getUsers():
    return get_fb_instance().child("users").get().each()


def deleteUser(data, *method):
    try:
        users = getUsers()
        if(len(method) == 0 or method[0] == "username"):
            user = [x for x in users if parseUser(
                x).username == data or parseUser(x).email == data][0]
            get_fb_instance().child("users").child(parseUser(user).username).remove()
            get_fb_instance().child("notes").child(parseUser(user).id).remove()
            return "User succesfuly deleted"
        elif(method[0] == "id"):
            user = [x for x in users if str(parseUser(x).id) == str(data)][0]
            get_fb_instance().child("users").child(parseUser(user).username).remove()
            get_fb_instance().child("notes").child(data).remove()
            return "User succesfuly deleted"
    except IndexError:
        return "Error: User not found"


def getUser(id):
    try:
        users = get_fb_instance().child("users").get().each()
        return parseUser([x for x in users if parseUser(x).id == id][0])
    except IndexError:
        return None


def getRawUser(id):
    users = getUsers()
    return [x for x in users if parseUser(x).id == id][0]


def updateUser(id, user_object):
    user = getUser(id)
    get_fb_instance().child("users").update(
        {user.username: json.dumps(user_object.__dict__)})


def updateChild(key, child, data):
    get_fb_instance().child(child).update({key: json.dumps(data)})


def createID():  # Fix session hangaround with deleted ID and jump to new users bug.
    if(getUsers() is not None):
        ID = -1
        if(getUsers() is not None):
            ID = len(getUsers())
        taken = "1"
        while len(taken) > 0:
            ID += 1
            taken = [x for x in getUsers() if parseUser(x).id == ID]
        return ID
    else:
        return 0


def getNotes(id):
    try:
        notes = get_fb_instance().child("notes").get().each()
        if(notes is not None):
            note = [x for x in notes if str(x.key()) == str(id)][0]
            if(note.val() is not None):
                note = base64.b64decode(note.val()[1:-1]).decode()
                return note
            else:
                return ""
        else:
            return ""
    except IndexError:
        return ""


def userExists(session):
    if(session.get('user_id') is not None):
        user_id = session.get('user_id')
        users = getUsers()
        exists = len([x for x in users if str(
            parseUser(x).id) == str(user_id)]) > 0
        return exists

def idExists(user_id):
    if(len([x for x in getUsers() if str(parseUser(x).id) == str(user_id)]) != 0):
        return True
    else:
        return False
