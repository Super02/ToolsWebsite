from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_management import parseUser
import json

ph = PasswordHasher()

login_pages = Blueprint('login_pages', __name__)


@login_pages.route('/login', methods=['GET', 'POST'])
def login_page():
    if(request.method == 'POST'):
        return login(request.form['username'], request.form['password'])
    elif(request.method == 'GET'):
        return render_template("login.html")


def login(username: str, password: str):
    valid = False
    for user in get_fb_instance().child("users").get().each(): # Smarter implementation
        try:
            if(user.key() == username and ph.verify(parseUser(user.val()).password, password)):
                valid = True
        except VerifyMismatchError:
            pass
    if(valid):
        users = get_fb_instance().child("users").get().each()
        for x in users:
            if x.key() == username: 
                user = parseUser(x.val())
        session['user_id'] = user.id
        return redirect(url_for("index"))
    elif(valid == False):
        return render_template(
            "showtext.html",
            title="Login failure",
            text="Password or username incorrect!")
