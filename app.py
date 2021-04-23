from flask import Flask, render_template, request, flash, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from ssh import *
from forms import *
from load_data_utils import cutting_records, generate_plot

app = Flask(__name__)
app.secret_key = 'csse433'
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
            return "failed login; please log in"
        return redirect("http://127.0.0.1:5000/search")

    return render_template('login.html', form=login_form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_form_date = SearchFormDate()
    search_form_date_range = SearchFormDateRange()
    return render_template('search.html', form1=search_form_date, form2=search_form_date_range)


@app.route('/date_result', methods=['GET', 'POST'])
def date_result():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        date = int(request.form.get('date'))
        record = mongo.db.customer.find_one(
            {'user_id': customer_id, 'cashflows.report_date': date},
            {'user_id': 1, 'cashflows.$': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )
        if record is None:
            return "no record matched"
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
        record_cursor = mongo.db.customer.find_one(
            {'user_id': customer_id},
            {'user_id': 1, 'cashflows': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )
        if record_cursor is None:
            return "Found 0 record"
        profile_keys = ['user_id', 'sex', 'city', 'constellation']
        user_profile = {k: record_cursor.get(k) for k in profile_keys}
        cashflow_info = cutting_records(record_cursor['cashflows'], date1, date2)
        plot_data = generate_plot(cashflow_info)

        return render_template("date_range_result.html", user_profile=user_profile, cashflow_info=cashflow_info,
                               plot_data=plot_data)
    else:
        return "thanks"


if __name__ == '__main__':
    app.run(debug=True)
