from flask import Flask, request, render_template, session, redirect, url_for
import dotenv
from login import login_pages
from signup import signup_pages

app = Flask(__name__)
app.register_blueprint(login_pages)
app.register_blueprint(signup_pages)

print("Starting up")


@app.route('/')
def index():
    try:
        if session['user_id'] != None:
            return 'Welcome to buylist.'
        else:
            return redirect(url_for('login_pages.login_page'))
    except KeyError:
        return redirect(url_for('login_pages.login_page'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, host='localhost', use_reloader=True)
