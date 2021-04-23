from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request, flash
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from forms import *

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


# use check if user has the admin to db
def check_login_info(username, password):  # DONE: connect to mongodb
    try:
        cli = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/?authSource=admin')
        cli.server_info()
        return True
    except OperationFailure as err:
        print(err)
        return False


@app.route('/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not login_form.validate_on_submit():
            flash('miss info')
        if not check_login_info(username, password):
            flash('incorrect username or password')

    return render_template('login.html', form=login_form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_form_date = SearchFormDate()

    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        date = request.form.get('date')
        print(customer_id, date)
        if not search_form_date.validate_on_submit():
            flash('miss info')

    return render_template('search.html', form=search_form_date)


if __name__ == '__main__':
    app.run(debug=True)
