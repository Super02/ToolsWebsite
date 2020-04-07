from flask import Flask, request, render_template, session, redirect, url_for
import dotenv
import os
from login import login_pages
from signup import signup_pages
from user_management import parseUser, getUsers, userExists
from profile import profile_pages

app = Flask(__name__)
app.register_blueprint(login_pages)
app.register_blueprint(signup_pages)
app.register_blueprint(profile_pages)

app.secret_key = os.environ['app_key']


@app.before_request
def before_request_func():
    if(userExists(session) == False):
        session['user_id'] = None


@app.route('/')
def index():
    try:
        users = getUsers()
        if session['user_id'] is not None:
            try:
                user = [x for x in users if parseUser(
                    x).id == session['user_id']][0]
                return redirect(
                    url_for(
                        f"profile.profile",
                        user_id=parseUser(user).id))
            except (TypeError, IndexError):
                session['user_id'] = None
                return redirect(url_for('login_pages.login_page'))
        else:
            return redirect(url_for('login_pages.login_page'))
    except KeyError:
        return redirect(url_for('login_pages.login_page'))


if __name__ == '__main__':
    app.run(debug=True, host='localhost', use_reloader=True)
