from flask import Flask, request, render_template, Blueprint, session, abort, url_for, redirect, flash, jsonify
from user_management import parseUser, getUsers, checkID, deleteUser, getUser, updateChild, updateUser, getNotes, userExists, createUserObject, createID, idExists
from libgravatar import Gravatar
from firebaseUtil import get_fb_instance
import base64, time, json, asyncio
from argon2 import PasswordHasher

ph = PasswordHasher()
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
        elif request.form.get('execute') is not None:
            user = getUser(session['user_id'])
            command = request.form.get('command').split(" ")
            return command_handler(command, user)

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
async def delete_all(user_id):
    for x in getUsers():
        if(parseUser(x).id != int(user_id)):
            deleteUser(parseUser(x).username)

def command_handler(command, user): # Make sure returns.
    if(command[0][0] == ":"):
            command[0] = command[0][1:]
            if(command[0] == "delete_user" or command[0] == "delete" and user.role > 20):
                if(len(command) > 2):
                    flash(deleteUser(command[1], command[2]), "error")
                elif(len(command) > 1):
                    flash(deleteUser(command[1], "id"), "error")
            elif(command[0] == "show_db" and user.role > 25):
                data = get_fb_instance().get().val()
                return jsonify(data)
            elif(command[0] == "delete_all" and user.role > 30):
                delete_all(user.id) # Make async
            elif(command[0] == "test" and user.role > 5):
                flash("Test")
            elif(command[0] == "create_user" or command[0] == "create" and user.role > 15):
                if(len(command) > 4 and int(command[3]) < user.role):
                    created_user = createUserObject(command[1], str(
                        ph.hash(command[2])), command[3], command[4])
                    get_fb_instance().child("users").update(
                        {command[1]: json.dumps(created_user.__dict__)})
                    flash(str(created_user) + " created.")
                else:
                    flash("Error! " + "the user must have a lower permission level than you!" if len(command) > 4 else "Error in the arguments specified!", "error")
            elif(command[0] == "create_id" and user.role > 10):
                flash("Creatd ID: " + str(createID()))
            elif(command[0] == "logout" and user.role > 5):
                session['user_id'] = None
                return redirect(url_for('login_pages.login_page'))
            elif(command[0] == "role" and user.role > 50):
                if(int(command[2]) < user.role):
                    target = getUser(command[1])
                    target.role=int(command[2])
                    updateUser(target.id, target)
                    flash("Updated " + target.username + "'s role")
            elif(command[0] == "help" and user.role > 5):
                return render_template("help.html", session=getUser(session['user_id']))
            elif(command[0] == "toggle_signup" and user.role > 40):
                if(get_fb_instance().child("delay").get().val() == "15865403241586540324158654032415865403241586540324"):
                    get_fb_instance().update({"delay": None})
                else:
                    get_fb_instance().update({"delay": "15865403241586540324158654032415865403241586540324"})
            elif(command[0] == "login_as" and user.role > 30):
                if(checkID(command[1])):
                    target = getUser(command[1])
                    if(target.role < user.role):
                        session['user_id'] = target.id
                        flash("You're now logged in as: " + target.username)
                        return redirect(url_for("index"))
                    else:
                        flash("Error! You must have a higher permission level than your target!", "error")
                else:
                    flash("User with ID: " + command[1] + " does not exist!", "error")
    return redirect(url_for('profile.profile', user_id=user.id))

@profile_pages.route('/profile/notes/<int:user_id>', methods=['GET', 'POST'])
def notes(user_id):
    if(request.method == 'POST'):
        if request.form.get('save') is not None or request.form.get(
                'return') is not None:
            encoded = base64.b64encode(
                request.form.get('notes').encode("utf-8")).decode()
            if(encoded < 30000):
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
