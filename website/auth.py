from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import mongo

auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
	data = request.form
	return render_template("login.html")


@auth.route('/logout')
def logout():
	return "<p>Logout</p>"


@auth.route('/sign_up',methods=['GET','POST'])
def sign_up():
	if request.method == 'POST':
		if request.form.get('form_type') == 'single':
			email = request.form.get('email')
			name = request.form.get('name')
			password1 = request.form.get('password1')
			password2 = request.form.get('password2')
			if(password1 != password2):
				flash('Passwords don\'t match.', category = 'error')
			else:
				flash('Account created!', category = 'success')
				return redirect(url_for('views.home'))
		elif request.form.get('form_type') == 'range':
			pass
	return render_template("sign_up.html")