from flask import Flask, request, render_template, Blueprint, session, abort
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

login_pages = Blueprint('login_pages',__name__)


@login_pages.route('/login', methods=['GET', 'POST'])
def login_page():
    if(request.method == 'POST'):
        return login(request.form['username'], request.form['password'])
    elif(request.method == 'GET'):  
        return render_template("login.html")

def login(username : str, password : str):  
    valid = False
    print(ph.hash(password))
    for user in get_fb_instance().child("users").get().each():
        try:
            if(user.key() == username and ph.verify(user.val(), password)):
                valid= True
        except VerifyMismatchError:
            pass
    if(valid==True):
        # Add session.
        return render_template("showtext.html", title="Login success", text="Welcome, you have successfuly logged in. This page is under construction. Please check back later.")
    elif(valid==False):
        return render_template("showtext.html", title="Login failure", text="Password or username incorrect!")