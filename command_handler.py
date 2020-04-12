from flask import flash, jsonify, session, redirect, url_for, render_template
from user_management import deleteUser, get_fb_instance, createUserObject, createID, getUser, updateUser, parseUser, getUsers, checkID
import json, asyncio
from argon2 import PasswordHasher

ph = PasswordHasher()

def handle_command(command, user):  # Make sure returns.
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
            delete_all(user.id)  # Make async
        elif(command[0] == "test" and user.role > 5):
            flash("Test")
        elif(command[0] == "create_user" or command[0] == "create" and user.role > 15):
            if(len(command) > 4 and int(command[3]) < user.role):
                created_user = createUserObject(command[1], str(
                    ph.hash(command[2])), command[3], command[4])
                get_fb_instance().child("users").update(
                    {created_user.id: json.dumps(created_user.__dict__)})
                flash(str(created_user) + " created.")
            else:
                flash("Error! " + "the user must have a lower permission level than you!" if len(
                    command) > 4 else "Error in the arguments specified!", "error")
        elif(command[0] == "create_id" and user.role > 10):
            flash("Creatd ID: " + str(createID()))
        elif(command[0] == "logout" and user.role > 5):
            session['user_id'] = None
            return redirect(url_for('login_pages.login_page'))
        elif(command[0] == "role" and user.role > 50):
            if(int(command[2]) < user.role):
                target = getUser(command[1])
                target.role = int(command[2])
                updateUser(target.id, target)
                flash("Updated " + target.username + "'s role")
        elif(command[0] == "help" and user.role > 5):
            return render_template(
                "help.html", session=getUser(
                    session['user_id']))
        elif(command[0] == "toggle_signup" and user.role > 40):
            if(get_fb_instance().child("delay").get().val() == "15865403241586540324158654032415865403241586540324"):
                get_fb_instance().update({"delay": None})
            else:
                get_fb_instance().update(
                    {"delay": "15865403241586540324158654032415865403241586540324"})
        elif(command[0] == "login_as" and user.role > 30):
            if(checkID(command[1])):
                target = getUser(command[1])
                if(target.role < user.role):
                    session['user_id'] = target.id
                    flash("You're now logged in as: " + target.username)
                    return redirect(url_for("index"))
                else:
                    flash(
                        "Error! You must have a higher permission level than your target!",
                        "error")
            else:
                flash(
                    "User with ID: " +
                    command[1] +
                    " does not exist!",
                    "error")
        elif(command[0] == "update_user" and user.role > 1336):
            if(len(command) > 3):
                if(checkID(command[1])):
                    user = getUser(command[1])
                    _type=command[4] if len(command) > 4 else "str"
                    setattr(user, command[2], int(command[3]) if _type == "int" else command[3])
                    updateUser(command[1], user)
                else:
                    flash("User not found", "error")
    return redirect(url_for('profile.profile', user_id=user.id))


async def delete_all(user_id):
    for x in getUsers():
        if(parseUser(x).id != int(user_id)):
            deleteUser(parseUser(x).username)