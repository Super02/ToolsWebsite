from flask import Flask, request, render_template
import dotenv
from login import login_pages

app = Flask(__name__)
app.register_blueprint(login_pages)

print("Starting up")


@app.route('/')
def index():
    return 'Welcome to buylist. To see your buylist please login.'


if __name__ == '__main__':
    app.run(debug=True, host='localhost', use_reloader=True)
