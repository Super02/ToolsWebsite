from flask import Flask, request, render_template, Blueprint, session, abort
from firebaseUtil import get_fb_instance
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

signup_pages = Blueprint('signup_pages', __name__)


@signup_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():
	if(request.method == 'POST'):
		return signup(request.form['username'], request.form['password'])
	elif(request.method == 'GET'):  
		return render_template("signup.html")

def signup(username : str, password : str):  
	taken=False
	for user in get_fb_instance().child("users").get().each():
		print(user.key())
		if(user.key()==username): taken=True # Change later for better integration
	if taken:
		return render_template("showtext.html", title="Signup failure", text="Username already taken")
	else:
		try:
			get_fb_instance().child("users").update({username : str(ph.hash(password))})
		except Exception as e:
			print(e)
			return render_template("showtext.html", title="Signup failure", text="An unknown error occured.")
		return render_template("showtext.html", title="Signup success", text="You have successfuly signed up. This page is under construction. Please check back later.")
