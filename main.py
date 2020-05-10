from flask import Flask, request, render_template, session, redirect, url_for
import dotenv
import os
import requests
import nexmo
import json
from datetime import datetime, timedelta
from login import login_pages
from signup import signup_pages
from user_management import parseUser, getUsers, userExists, get_fb_instance, updateRawChild
from profile import profile_pages
from autosms import autosms
from flask_googlecharts import GoogleCharts, MaterialLineChart
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.register_blueprint(login_pages)
app.register_blueprint(signup_pages)
app.register_blueprint(profile_pages)
app.register_blueprint(autosms)
charts = GoogleCharts(app)

scheduler = BackgroundScheduler()

client = nexmo.Client(
    key=os.environ['nexmo_key'],
    secret=os.environ['nexmo_secret'])
app.secret_key = os.environ['app_key']


def checkSMS():
    for x in get_fb_instance().child("smses").get().each():
        if(x.val() is None):
            continue
        pending = x.val()["pending"]
        date = datetime.strptime(pending["date"], "%dth %B %Y").date()
        now = datetime.now().date()
        if(now == date and datetime.now().hour > 14):
            print(x.val())
            messsage = client.send_message(
                {
                    'from': x.val()["pending"]["src"],
                    'to': "45" + x.val()["pending"]["dst"],
                    'text': x.val()["pending"]["message"]})
            print(messsage)
            updateRawChild("smses",
                           "smses/{}".format(x.key()),
                           x.val()["smses"] - 1)
            if(pending["repeat"] == "-1"):
                get_fb_instance().child("smses/{}/pending".format(x.key())).remove()
                print("Message sent")
            else:
                updateRawChild(
                    "date",
                    "smses/{}/pending".format(
                        x.key()),
                    datetime.strftime(
                        date +
                        timedelta(
                            days=int(
                                pending["repeat"])),
                        "%dth %B %Y"))
                print("Message sent and next message scheduled.")


scheduler.add_job(func=checkSMS, trigger="interval", hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route('/api/check/sms', methods=["POST", "GET"])
def smsCheckApi():
    checkSMS()
    return "200 Sucess", 200


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
