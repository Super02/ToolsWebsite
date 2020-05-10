from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_management import parseUser, getUsers, updateRawChild, updateUser
import json, uuid, time, re, requests, os

ph = PasswordHasher()

H_SECRET_KEY = os.environ['h_secret']
H_VERIFY_URL = "https://hcaptcha.com/siteverify"

login_pages = Blueprint('login_pages', __name__)

@login_pages.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if(request.method == 'POST'):
        data = {'secret': H_SECRET_KEY, 'response': request.form['h-captcha-response']}
        response = requests.post(url=H_VERIFY_URL, data=data)
        success = response.json()['success']
        if(not success):
            flash("You did not complete our captcha!")
            return render_template("forgot_password.html")
        email = request.form.get("email")
        sendResetEmail(email)
        print(f"Sent password reset request to: {email}")
        flash(f"Password Reset email sent to: {email}", "success")
        return redirect(url_for("login_pages.login_page"))
    return render_template("forgot_password.html")


def sendResetEmail(email):
    users = getUsers()
    user = [x for x in users if str(parseUser(x).email) == str(email)]
    epoch = time.time()
    if(len(user) > 0):
        user=parseUser(user[0])
        UUID = str(uuid.uuid3(uuid.NAMESPACE_DNS, email)) + str(uuid.uuid4()) + "--" + str(epoch+900)
        updateRawChild(user.id, "userdata/reset", UUID)
    

@login_pages.route('/reset/<token>', methods=['POST', 'GET'])
def reset_user(token):
    if(request.method == 'POST'):
        user = [x for x in get_fb_instance().child("userdata/reset").get().each() if x.val() == str(token)]
        try:
            epoch = user[0].val().split("--")[1]
        except(IndexError):
            flash("Error! Token expired or does not exist", "error")
            return redirect(url_for("login_pages.login_page"))
        now = time.time()
        if(len(user) > 0 and float(epoch) > now):
            user = parseUser([x for x in getUsers() if parseUser(x).id == user[0].key()][0])
            password = request.form.get("password")
            if(not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,200}$", password)):
                flash("Invalid password.", "error")
                return render_template('reset.html')
            user.password = ph.hash(request.form.get("password"))
            updateUser(user.id, user)
            flash("Password updated!", "success")
            get_fb_instance().child("userdata/reset/{}".format(user.id)).remove()
            return redirect(url_for("login_pages.login_page"))
        else:
            flash("Error! Token expired or does not exist.", "error")
            return redirect(url_for("login_pages.login_page"))
    return render_template('reset.html')
    

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
        flash("Username or password incorrect.", "error")
        return redirect(url_for("login_pages.login_page"))
