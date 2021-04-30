from flask import Blueprint, render_template, request
from . import mongo
import pandas as pd
import base64
from io import BytesIO
from matplotlib.figure import Figure

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
		
		return render_template("date_range_result.html", user_profile=user_profile, cashflow_info=cashflow_info,
							   plot_data=plot_data)
	else:
		return "WTF"


def cutting_records(cashflows,date1,date2):
    copy = cashflows.copy()
    for record in cashflows:
            if(record['report_date']<date1 or record['report_date']>date2):
                copy.remove(record)
    return copy


def generate_plot(cashflows):
    plot_df = pd.DataFrame()
    balance = [cashflow['balance']['tBalance'] for cashflow in cashflows]
    plot_df['balance'] = balance
    plot = Figure()
    ax = plot.subplots()
    plot_df.plot(ax=ax)
    buf = BytesIO()
    plot.savefig(buf, format='png')
    data = base64.b64encode(buf.getbuffer()).decode('ascii')
    return data