from flask import Flask, request, render_template, Blueprint, session, abort, redirect, url_for, flash
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_management import createUserObject, parseUser, getUsers
import json
import time

ph = PasswordHasher()

signup_pages = Blueprint('signup_pages', __name__)


@signup_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if(request.method == 'POST'):
        if request.form.get('removeFlash') is None:
            return signup(
                request.form['username'],
                request.form['password'],
                request.form['email'])
        else:
            return redirect(url_for("signup_pages.signup_page"))
    elif(request.method == 'GET'):
        return render_template("signup.html")


def signup(username: str, password: str, email: str):
    users = getUsers()
    if(users is not None):
        if(get_fb_instance().child("delay").get() is not None):
            if(float(get_fb_instance().child("delay").get().val()) + 10 < float(time.time())):
                get_fb_instance().update({"delay": str(time.time())})
            else:
                flash(
                    "Too many users are signing up right now! Please try again later.",
                    "error")
                return redirect(url_for("signup_pages.signup_page"))
        else:
            get_fb_instance().update({"delay": str(time.time())})
    if users is not None and [x for x in users if x.key().lower(
    ) == username.lower() or parseUser(x).email.lower() == email.lower()]:
        flash("Username or email already taken!", "error")
        return redirect(url_for("signup_pages.signup_page"))
    else:
        try:
            user = createUserObject(username, str(ph.hash(password)), 0, email)
            get_fb_instance().child("users").update(
                {username: json.dumps(user.__dict__)})
            session['user_id'] = user.id
            return redirect(url_for("index"))
        except Exception as e:
            print(e)
            flash("An unknown error occured!", "error")
            return redirect(url_for("signup_pages.signup_page"))
