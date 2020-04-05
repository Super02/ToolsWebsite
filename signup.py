from flask import Flask, request, render_template, Blueprint, session, abort, redirect, url_for
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from user_management import createUserObject, parseUser
import json

ph = PasswordHasher()

signup_pages = Blueprint('signup_pages', __name__)


@signup_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():
	if(request.method == 'POST'):
		return signup(request.form['username'], request.form['password'])
	elif(request.method == 'GET'):  
		return render_template("signup.html")

def signup(username : str, password : str):  
	users = get_fb_instance().child("users").get().each()
	if users != None and [x for x in users if x.key() == username]:
		return render_template("showtext.html", title="Signup failure", text="Username already taken")
	else:
		try:
			user=createUserObject(username, str(ph.hash(password)), "Member")
			get_fb_instance().child("users").update({username : json.dumps(user.__dict__)})
			session['user_id'] = user.id
			return redirect(url_for("index"))
		except Exception as e:
			print(e)
			return render_template("showtext.html", title="Signup failure", text="An unknown error occured.")
