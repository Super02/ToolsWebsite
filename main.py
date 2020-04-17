from flask import Flask, request, render_template, session, redirect, url_for
import dotenv
import os
import requests
from login import login_pages
from signup import signup_pages
from user_management import parseUser, getUsers, userExists
from profile import profile_pages
from flask_googlecharts import GoogleCharts, MaterialLineChart


app = Flask(__name__)
app.register_blueprint(login_pages)
app.register_blueprint(signup_pages)
app.register_blueprint(profile_pages)
charts = GoogleCharts(app)


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


@app.route(
    '/profile/corona/<int:user_id>',
    methods=[
        'GET',
        'POST'])  # Move to profile blueprint
def corona_page(user_id):
    BASE_URL = "https://pomber.github.io/covid19/timeseries.json"
    countries = [
        "Denmark",
        "Norway",
        "Sweden",
        "US",
        "Italy",
        "China",
        "Spain"]
    r = requests.get(BASE_URL).json()
    datalength = len([x["date"] for x in r[countries[0]]])
    full = False

    zoom = session.get('zoom') if session.get('zoom') is not None else 31
    if request.method == "POST":
        if(request.form.get("slider") is not None):
            zoom = int(request.form.get("slider"))
        if(request.form.get("fulldata") is not None):
            full = True
    # Make sure if length is not the same to: Improve to find date of longest
    # country data
    dates = [x["date"] for x in r[countries[0]]][-zoom:]
    corona_chart = MaterialLineChart(
        "corona",
        options={
            "title": "Corona chart",
            "width": 1200,
            "height": 800})
    corona_chart.add_column("string", "Date")
    for country in countries:
        corona_chart.add_column("number", country)
    for i, date in enumerate(dates):
        row_data = [date]
        for country in countries:
            if(full != True):
                row_data.append([j["deaths"] - x["deaths"]
                                 for x, j in zip(r[country], r[country][1:])][-zoom:][i])
            else:
                row_data.append([x["deaths"] for x in r[country]][-zoom:][i])
        corona_chart.add_rows([row_data])
    charts.register(corona_chart)
    session['zoom'] = zoom
    return render_template(
        'corona_page.html',
        datalength=datalength - 2,
        zoom=zoom,
        countries=countries)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', use_reloader=True)
