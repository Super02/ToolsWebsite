from flask import Flask, request, render_template, Blueprint, session, abort, redirect, url_for, flash
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_management import createUserObject, parseUser, getUsers, getUser
import time
import os
import requests
import re
import json

ph = PasswordHasher()

signup_pages = Blueprint('signup_pages', __name__)
H_SECRET_KEY = os.environ['h_secret']
H_VERIFY_URL = "https://hcaptcha.com/siteverify"



# SAVE DATA WHEN RELOADING PAGE


@signup_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if(request.method == 'POST'):
        if request.form.get('removeFlash') is None or request.form.get(
                'removeFlash') == '':
            return signup(
                request.form['username'],
                request.form['password'],
                request.form['email'],
                request.form['h-captcha-response'])
        else:
            return redirect(url_for("signup_pages.signup_page"))
    elif(request.method == 'GET'):
        return render_template("signup.html")


def signup(username: str, password: str, email: str, token):
    data = {'secret': H_SECRET_KEY, 'response': token}
    response = requests.post(url=H_VERIFY_URL, data=data)
    success = response.json()['success']
    if(not re.match(r"^[a-zA-Z0-9_.+-]{1,70}@[a-zA-Z0-9-]{1,63}\.[a-zA-Z0-9-.]{2,3}$", email)):
        flash("Error! Email invalid.")
        return redirect(url_for("signup_pages.signup_page"))
    if(not re.match(r"^[a-zA-Z0-9_-]{1,32}$", username)):
        flash("Error! Username invalid.")
        return redirect(url_for("signup_pages.signup_page"))
    bypass = getUser(session.get('user_id')).role < 30 if session.get(
        'user_id') is not None else True
    if(not success and bypass):
        flash("Error! You did not complete our captcha!")
        return redirect(url_for("signup_pages.signup_page"))
    users = getUsers()
    if(users is not None):
        if(get_fb_instance().child("delay").get().val() is not None):
            if(float(get_fb_instance().child("delay").get().val()) + 10 < float(time.time())):
                get_fb_instance().update({"delay": str(time.time())})
            else:
                if(get_fb_instance().child("delay").get().val() == "15865403241586540324158654032415865403241586540324"):
                    flash("Signup has been closed by an administrator.", "error")
                else:
                    flash(
                        "Too many users are signing up right now! Please try again later.",
                        "error")
                return redirect(url_for("signup_pages.signup_page"))
        else:
            get_fb_instance().update({"delay": str(time.time())})
    if users is not None and [x for x in users if parseUser(x).username.lower(
    ) == username.lower() or parseUser(x).email.lower() == email.lower()]:
        flash("Username or email already taken!", "error")
        return redirect(url_for("signup_pages.signup_page"))
    if(not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,200}$", password)):
        flash("Invalid password.", "error")
        return redirect(url_for("signup_pages.signup_page"))
    else:
        try:
            user = createUserObject(username, str(ph.hash(password)), 0, email)
            get_fb_instance().child("users").update(
                {str(user.id): json.dumps(user.__dict__)})
            session['user_id'] = user.id
            return redirect(url_for("index"))
        except Exception as e:
            print(e)
            flash("An unknown error occured!", "error")
            return redirect(url_for("signup_pages.signup_page"))
