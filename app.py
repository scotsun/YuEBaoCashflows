from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from pymongo.errors import OperationFailure

app = Flask(__name__)
app.secret_key = 'csse433'


# use connect to mongodb
def check_login_info(username, password):  # TODO: connect to mongodb
    host = "localhost"
    port = 27017
    try:
        # TODO: set for local for test and debug
        cli = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/?authSource=admin')
        cli.server_info()
        return True
    except OperationFailure as err:
        print(err)
        return False


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not login_form.validate_on_submit():
            flash('miss info')
        elif not check_login_info(username, password):
            flash('incorrect username or password')
        else:
            return 'success'

    return render_template('login.html', form=login_form)


if __name__ == '__main__':
    app.run(debug=True)
