from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request, flash
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pprint import pprint
from forms import *

app = Flask(__name__)
app.secret_key = 'csse433'
tunnel = SSHTunnelForwarder(
        "34.67.124.229",
        ssh_username="sfeng",
        ssh_pkey="~/.ssh/id_rsa.pub",
        ssh_private_key_password="",
        remote_bind_address=("127.0.0.1", 27017)
    )
tunnel.start()
host = "localhost"
port = tunnel.local_bind_port
app.config['MONGO_URI'] = f'mongodb://{host}:{port}/yuebao'
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
    search_form_date_range = SearchFormDateRange()
    if request.method == 'POST' or request.method == 'GET':
        # customer_id = request.form.get('customer_id')
        # date = request.form.get('date')
        #
        # if search_form_date.validate_on_submit():
        #     customer_id = int(customer_id)
        #     date = int(date)
        #
        # print(customer_id, date)
        # result = mongo.db.customer.find_one(
        #     {'user_id': customer_id, 'cashflows.report_date': date},
        #     {'user_id': 1, 'cashflows.$': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        # )
        # pprint(result)
        return render_template('search.html', form1=search_form_date, form2=search_form_date_range)
    else:
        return "go back"


@app.route('/date_result', methods=['GET', 'POST'])
def date_result():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        date = int(request.form.get('date'))
        record = mongo.db.customer.find_one(
            {'user_id': customer_id, 'cashflows.report_date': date},
            {'user_id': 1, 'cashflows.$': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )

        profile_keys = ['user_id', 'sex', 'city', 'constellation']
        user_profile = {k: record.get(k) for k in profile_keys}

        cashflow_info = record['cashflows'][0]
        return render_template("date_result.html", user_profile=user_profile, cashflow_info=cashflow_info)
    else:
        return "go back"


@app.route('/date_range_result', methods=['GET', 'POST'])
def date_range_result():
    if request.method == "POST":
        customer_id = int(request.form.get('customer_id'))
        date1 = int(request.form.get('date1'))
        date2 = int(request.form.get('date2'))
        recordCursor = mongo.db.customer.find_one(
            {'user_id': customer_id},
            {'user_id': 1, 'cashflows': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )
        if(recordCursor == None):
            return "Found 0 record"
        profile_keys = ['user_id', 'sex', 'city', 'constellation']
        user_profile = {k: recordCursor.get(k) for k in profile_keys}
        cashflow_info = cutting_records(recordCursor['cashflows'],date1,date2)
        
        return render_template("date_range_result.html", user_profile=user_profile, cashflow_info=cashflow_info)
    else:
        return "thanks"

#To slice records that are within range
def cutting_records(cashflows,date1,date2):
    copy = cashflows.copy()
    for record in cashflows:
            if(record['report_date']<date1 or record['report_date']>date2):
                copy.remove(record)
    return copy


if __name__ == '__main__':
    app.run(debug=True)
