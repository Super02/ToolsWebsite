from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash
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
        if request.form.get('removeFlash') is None:
            return login(
                request.form['username_email'],
                request.form['password'])
        else:
            return redirect(url_for("login_pages.login_page"))
    elif(request.method == 'GET'):
        return render_template("login.html")


def login(username: str, password: str):
    users = get_fb_instance().child("users").get().each()
    try:
        user = [x for x in users if parseUser(x).username.lower(
        ) == username.lower() or parseUser(x).email.lower() == username.lower()][0]
    except (IndexError, TypeError):
        flash("Username or password incorrect.", "error")
        return redirect(url_for("login_pages.login_page"))
    user = parseUser(user)
    try:
        if(user and ph.verify(user.password, password)):
            session['user_id'] = user.id
            return redirect(url_for("index"))
        else:
            flash("Username or password incorrect.", "error")
            return redirect(url_for("login_pages.login_page"))
    except VerifyMismatchError:
        pass
