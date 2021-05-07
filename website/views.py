from flask import Blueprint, render_template, request, session
from . import mongo
from .forecasting import *
from .load_data_utils import cutting_records, generate_plot

views = Blueprint('views',__name__)


@views.route('/')
def home():
	return render_template("home.html")


@views.route('/search',methods=['GET','POST'])
def search():	
	return render_template("search.html")


@views.route('/date_result',methods=['POST'])
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


@views.route('/date_range_result',methods=['GET','POST'])
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
		cashflow_info = cutting_records(recordCursor['cashflows'], date1, date2)
		plot_data = generate_plot(cashflow_info)
		session['customer_id'] = customer_id
		session['overall_cashflow_info'] = recordCursor['cashflows']
		return render_template("date_range_result.html", user_profile=user_profile, cashflow_info=cashflow_info,
							   plot_data=plot_data)
	else:
		return "WTF"

@views.route('/customer_result',methods=['POST'])
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
			print(city)
		if constellation != '':
			query['constellation'] = constellation
		if sex != '':
			query['sex'] = sex

		print(query)

		customer_records = list(mongo.db.customer.find(query, {'cashflows': 0, '_id': 0}))
		num_customer_records = len(customer_records)
		return render_template("customer_result.html", num_customer_records=num_customer_records,
							   customer_records=customer_records)
	else:
		return "WTF"



@views.route('/forecast_result', methods=['POST'])
def forecast_result():
	if request.method == 'POST':
		customer_id = session.get('customer_id', None)
		overall_cashflow_info = session.get('overall_cashflow_info', None)

		if len(overall_cashflow_info) <= 15:
			return "less than 15 days of record; we cannot forecast"

		num_future_dates = int(request.form.get('num_future_steps'))
		forecast_plot_data = auto_arima_forecasting(overall_cashflow_info, num_future_dates)

		return render_template("forecast_result.html", customer_id=customer_id,
							   num_future_dates=num_future_dates, forecast_plot_data=forecast_plot_data)
	else:
		return "please go back"