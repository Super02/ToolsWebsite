from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash
from user_management import getUserSmSes, updateRawChild, get_fb_instance


autosms = Blueprint('autosms', __name__)

@autosms.route('/autosms', methods=['GET', 'POST'])
def auto_sms():
    smses = getUserSmSes(session.get("user_id"))
    if(smses != None and smses > 0):
        if request.method == "POST":
            for x in ["repeat", "message", "date", "dst", "src"]:
                updateRawChild(x, "smses/{}/pending".format(session.get("user_id")), request.form.get(x))
        if(smses != None and smses > 0):
            return render_template('autosms.html')
    else:
        return render_template("showtext.html", title="403", text="Permission denied.")