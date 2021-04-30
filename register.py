from passlib.has import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

#register form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Two Passwords are not same')
    ])
    confirm = PasswordField('Confirm Password')
