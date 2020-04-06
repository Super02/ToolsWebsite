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
    users = get_fb_instance().child("users").get().each()
    try:
        user = [x for x in users if parseUser(x.val()).username == username][0]
    except IndexError:
        return render_template(
            "showtext.html",
            title="Login failure",
            text="Password or username incorrect!")
    user = parseUser(user.val())
    try:
        if(user and ph.verify(user.password, password)):
            session['user_id'] = user.id
            return redirect(url_for("index"))
        else:
            return render_template(
                "showtext.html",
                title="Login failure",
                text="Password or username incorrect!")
    except VerifyMismatchError:
        pass
