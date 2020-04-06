from flask import Flask, request, render_template, session, redirect, url_for
import dotenv
from login import login_pages
from signup import signup_pages
from user_management import parseUser, getUsers

app = Flask(__name__)
app.register_blueprint(login_pages)
app.register_blueprint(signup_pages)

print("Starting up")

# Make role as integer
@app.route('/', methods=['GET', 'POST'])
def index():
    if(request.method == 'POST'):
        session['user_id'] = None
        return redirect(url_for('login_pages.login_page'))
    else:
        try:
            users = getUsers()
            if session['user_id'] != None:
                user = [x for x in users if parseUser(x).id == session['user_id']][0]
                return render_template('index.html', user=parseUser(user))
            else:
                return redirect(url_for('login_pages.login_page'))
        except KeyError:
            return redirect(url_for('login_pages.login_page'))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, host='localhost', use_reloader=True)
