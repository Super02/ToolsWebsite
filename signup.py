from flask import Flask, request, render_template, Blueprint, session, abort
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

signup_pages = Blueprint('signup_pages', __name__)


@signup_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if(request.method == 'POST'):
        return signup(request.form['username'], request.form['password'])
    elif(request.method == 'GET'):
        return render_template("signup.html")


def signup(username: str, password: str):
    if username in get_fb_instance().child("users").get().each():
        return render_template(
            "showtext.html",
            title="signup failure",
            text="Username already taken")
    else:
        get_fb_instance.child("users").push("name": "", )
        return render_template(
            "showtext.html",
            title="signup success",
            text="You have successfuly signed up. This page is under construction. Please check back later.")
