from flask import Blueprint, render_template, request, session, redirect
from . import mongo
from . import cassandra
from .forecasting import *
from .load_data_utils import generate_plot, generate_dataframe, get_group_mean_result

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html")


@views.route('/search', methods=['GET', 'POST'])
def search():
    return render_template("search.html")


@views.route('/date_result', methods=['POST'])
def date_result():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id1'))
        date = int(request.form.get('date'))
        record = mongo.db.customer.find_one_or_404(
            {'user_id': customer_id, 'cashflows.report_date': date},
            {'user_id': 1, 'cashflows.$': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )
        profile_keys = ['user_id', 'sex', 'city', 'constellation']
        user_profile = {k: record.get(k) for k in profile_keys}
        cashflow_info = record['cashflows'][0]
        return render_template("date_result.html", user_profile=user_profile, cashflow_info=cashflow_info)
    else:
        return "WTF"


@views.route('/date_range_result', methods=['GET', 'POST'])
def date_range_result():
    if request.method == "POST":
        customer_id = int(request.form.get('customer_id2'))
        date1 = int(request.form.get('date1'))
        date2 = int(request.form.get('date2'))
        recordCursor = mongo.db.customer.find_one_or_404(
            {'user_id': customer_id},
            {'user_id': 1, 'cashflows': 1, 'sex': 1, 'city': 1, 'constellation': 1, '_id': 0}
        )
        profile_keys = ['user_id', 'sex', 'city', 'constellation']
        user_profile = {k: recordCursor.get(k) for k in profile_keys}

        cql = f"""
        select report_date, tbalance, total_purchase_amt, total_redeem_amt from user_balance 
        where user_id = {customer_id} and report_date >= {date1} and report_date <= {date2};
        """
        cashflow_info = list(cassandra.execute(cql))
        cashflow_info_df = generate_dataframe(cashflow_info)
        plot_data = generate_plot(cashflow_info_df)
        session['customer_id'] = customer_id
        session['overall_cashflow_info'] = cashflow_info
        return render_template("date_range_result.html", user_profile=user_profile, cashflow_info=cashflow_info,
                               plot_data=plot_data)
    else:
        return "WTF"


@views.route('/customer_result', methods=['POST'])
def customer_result():
    if request.method == 'POST':
        city = request.form.get('city_label')
        constellation = request.form.get('constellation_label')
        sex = request.form.get('sex')
        if sex != '':
            try:
                sex = int(sex)
            except ValueError:
                pass

        query = {}
        if city != '':
            query['city'] = city
        if constellation != '':
            query['constellation'] = constellation
        if sex != '':
            query['sex'] = sex

        customer_records = list(mongo.db.customer.find(query, {'cashflows': 0, '_id': 0}))
        customer_ids = tuple(elem['user_id'] for elem in customer_records)
        num_customer_records = len(customer_ids)
        cql = f"""
        select report_date, tbalance, total_purchase_amt, total_redeem_amt from user_balance 
        where user_id in {customer_ids};
        """
        cashflow_info = list(cassandra.execute(cql))
        group_mean_df = get_group_mean_result(cashflow_info)
        plot_data = generate_plot(group_mean_df)
        return render_template("customer_result.html", num_customer_records=num_customer_records,
                               customer_records=customer_records, plot_data=plot_data)
    else:
        return "WTF"


@views.route('/forecast_result', methods=['POST', 'GET'])
def forecast_result():
    if request.method == 'POST':
        customer_id = session.get('customer_id', None)
        overall_cashflow_info = session.get('overall_cashflow_info', None)
        overall_cashflow_df = generate_dataframe(overall_cashflow_info)

        if len(overall_cashflow_info) <= 15:
            return "less than 15 days of record; we cannot forecast"

        num_future_dates = int(request.form.get('num_future_steps'))
        forecast_plot_data, arima_order = auto_arima_forecasting(overall_cashflow_df['tbalance'], num_future_dates,
                                                                 'balance')
        acf_plot_data = get_acf_plot(overall_cashflow_df['tbalance'])
        pacf_plot_data = get_pacf_plot(overall_cashflow_df['tbalance'])
        return render_template("forecast_result.html", customer_id=customer_id, arima_order=arima_order,
                               num_future_dates=num_future_dates, forecast_plot_data=forecast_plot_data,
                               acf_plot_data=acf_plot_data, pacf_plot_data=pacf_plot_data)
    else:
        return redirect("http://127.0.0.1:5000/search")
