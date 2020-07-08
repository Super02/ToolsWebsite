from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash, jsonify
from flask import current_app as app
from user_management import getUser

buylist_pages = Blueprint('buylist_page', __name__)


@buylist_pages.route('/buylist_page/<int:user_id>', methods=['GET', 'POST'])
def buylist_page(user_id):
    if(request.method == 'POST'):
        return render_template(
            "showtext.html",
            title="400",
            text="400: Post requests are denied")
    else:
        if(session.get('user_id') is not None):
                if(session['user_id'] == user_id or getUser(session['user_id']).role > getUser(user_id).role):
                    return render_template("buylist.html", user=getUser(user_id), session=getUser(session['user_id']))
        return render_template(
            "showtext.html",
            title="401",
            text="401: User not allowed")