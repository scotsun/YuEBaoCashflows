from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import mongo
from .model import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		user = User.get_by_email(email)
		if user:
			if check_password_hash(user.password, password):
				flash('Logged in successfully!', category='success')
				login_user(user, remember=True)
				return redirect(url_for('views.home'))
			else:
				flash('Incorrect password, try again.', category='error')
		else:
			flash('Email does not exist.', category='error')
	return render_template("login.html")


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('auth.login'))


@auth.route('/sign_up',methods=['GET','POST'])
def sign_up():
	if request.method == 'POST':
		email = request.form.get('email')
		username = request.form.get('username')
		password1 = request.form.get('password1')
		password2 = request.form.get('password2')
		if(password1 != password2):
			flash('Passwords don\'t match.', category = 'error')
		else:
			password = generate_password_hash(password1,method='sha256')
			User.register(username,email,password)
			flash('Account created!', category = 'success')
			return redirect(url_for('views.home'))
	return render_template("sign_up.html")