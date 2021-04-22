from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from pymongo.errors import OperationFailure

app = Flask(__name__)
app.secret_key = 'csse433'
tunnel = SSHTunnelForwarder(
        "34.67.124.229",
        ssh_username="apple",
        ssh_pkey="/Users/apple/Desktop/CSSE433/project-cli-keys/key-instance-1",
        ssh_private_key_password="csse433",
        remote_bind_address=("127.0.0.1", 27017)
    )
tunnel.start()
host = "localhost"
port = tunnel.local_bind_port
app.config['MONGO_URI'] = f'mongodb://{host}:{port}/?authSource=admin'
mongo = PyMongo(app)


# use connect to mongodb
def check_login_info(username, password):  # TODO: connect to mongodb
    try:
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
