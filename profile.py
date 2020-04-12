from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash, jsonify
from user_management import deleteUser, getUser, idExists, getUsers, parseUser, updateChild, getNotes
from libgravatar import Gravatar
from firebaseUtil import get_fb_instance
import base64
import time
import json
from command_handler import handle_command

profile_pages = Blueprint('profile', __name__)


@profile_pages.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if(request.method == 'POST'):
        if request.form.get('logout') is not None:
            session['user_id'] = None
            return redirect(url_for('login_pages.login_page'))
        elif request.form.get('notes') is not None:
            return redirect(url_for('profile.notes', user_id=user_id))
        elif request.form.get('removeFlash') is not None:
            return redirect(url_for("profile.profile", user_id=user_id))
        elif request.form.get('delete_user'):
            flash(deleteUser(user_id, "id"), "error")
            return redirect(url_for("index"))
        elif request.form.get('execute') is not None:
            user = getUser(session['user_id'])
            command = request.form.get('command').split(" ")
            return handle_command(command, user)

        return redirect(url_for('profile.profile', user_id=user_id))
    else:
        if(session.get('user_id') is not None):
            if(idExists(user_id) == False):
                return render_template(
                    "showtext.html",
                    title="404",
                    text="404: User not found")
            if(session['user_id'] == user_id or getUser(session['user_id']).role > 10):
                users = getUsers()
                user = getUser(user_id)
                userList = []
                for x in users:
                    userList.append(parseUser(x))
                return render_template(
                    'profile.html', session=getUser(
                        session['user_id']), user=parseUser(user), gravatar=Gravatar(
                        parseUser(user).email).get_image(), usersList=userList)
        return render_template(
            "showtext.html",
            title="401",
            text="401: User not allowed")


@profile_pages.route('/profile/notes/<int:user_id>', methods=['GET', 'POST'])
def notes(user_id):
    if(request.method == 'POST'):
        if request.form.get('save') is not None or request.form.get(
                'return') is not None:
            encoded = base64.b64encode(
                request.form.get('notes').encode("utf-8")).decode()
            if(len(request.form.get('notes')) < 30000):
                updateChild(user_id, "notes", encoded)
            else:
                flash("Save error! Your document must not exceed 30,000 characters!")
            if request.form.get('return') is not None:
                return redirect(url_for("profile.profile", user_id=user_id))
            else:
                return render_template(
                    "notes.html",
                    user=getUser(user_id),
                    notes=getNotes(user_id),
                    session=getUser(
                        session['user_id']))
        if request.form.get('removeFlash') is not None:
            return redirect(url_for("profile.notes", user_id=user_id))
    else:
        if(session.get('user_id') is not None):
            if(session['user_id'] == user_id or getUser(session['user_id']).role > getUser(user_id).role):
                return render_template(
                    "notes.html",
                    user=getUser(user_id),
                    notes=getNotes(user_id),
                    session=getUser(
                        session['user_id']))
