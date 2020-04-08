from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash
from user_management import parseUser, getUsers, deleteUser, getUser, updateChild, getNotes, userExists
from libgravatar import Gravatar
from firebaseUtil import get_fb_instance
import json
import base64

profile_pages = Blueprint('profile', __name__)


@profile_pages.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if(request.method == 'POST'):
        if request.form.get('logout') is not None:
            session['user_id'] = None
            return redirect(url_for('login_pages.login_page'))
        elif request.form.get('delete') is not None:
            flash(deleteUser(user_id, "id"))
            session['user_id'] = None
            return redirect(url_for('login_pages.login_page'))
        elif request.form.get('deleteall') is not None:
            for x in getUsers():
                if(parseUser(x).id != int(user_id)):
                    flash(deleteUser(parseUser(x).username))
        elif request.form.get('delete_user') is not None:
            flash(deleteUser(request.form.get("delete_username"), "id"))
        elif request.form.get('notes') is not None:
            return redirect(url_for('profile.notes', user_id=user_id))
        elif request.form.get('removeFlash') is not None:
            return redirect(url_for("profile.notes"))
        return redirect(url_for('profile.profile', user_id=user_id))
    else:
        if(session.get('user_id') is not None):
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
        if request.form.get('save') is not None:
            encoded = base64.b64encode(request.form.get('notes').encode("utf-8")).decode()
            updateChild(user_id, "notes", encoded)
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
            if(session['user_id'] == user_id or getUser(session['user_id']).role > 10):
                print(getNotes(user_id))
                return render_template(
                    "notes.html",
                    user=getUser(user_id),
                    notes=getNotes(user_id),
                    session=getUser(
                        session['user_id']))
