import os
import pyrebase
import dotenv

config = {
    "apiKey": os.environ["firebase_api_key"],
    "authDomain": os.environ["firebase_authdomain"],
    "databaseURL": os.environ["firebase_databaseurl"],
    "storageBucket": os.environ["firebase_storagebucket"]
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(
    os.environ["firebase_email"],
    os.environ["firebase_password"])
db = firebase.database()


def get_fb_instance():
    return db
