import pandas as pd
from . import mongo
from . import cassandra
from .load_data_utils import generate_plot, generate_dataframe, get_group_mean_result, \
	generate_blank_plot, generate_rate_plot
from .forecasting import auto_arima_forecasting


def generate_customer_cashflow_forecast_plot(customer_id, start_date, end_date, num_fdays):
	cql = f"""
			select report_date, tbalance, total_purchase_amt, total_redeem_amt from user_balance 
			where user_id = {customer_id} and report_date >= {start_date} and report_date <= {end_date};
			"""
	cashflow_info = list(cassandra.execute(cql))
	if not cashflow_info:
		plot_data = generate_blank_plot()
		return plot_data, tuple([0, 0, 0])
	cashflow_info = generate_dataframe(cashflow_info)
	forecast_plot_data, arima_order = auto_arima_forecasting(cashflow_info['tbalance'], num_fdays, 'balance')
	return forecast_plot_data, arima_order


def generate_group_daily_average_cashflow_plot(customer_properties, start_date, end_date):
	group_customer_records = list(mongo.db.customer.find(customer_properties, {'_id': 0}))
	group_customer_ids = tuple(elem['user_id'] for elem in group_customer_records)
	cql = f"""
			select report_date, tbalance, total_purchase_amt, total_redeem_amt from user_balance 
			where user_id in {group_customer_ids} and report_date >= {start_date} and report_date <= {end_date}
			"""

	cashflow_info = list(cassandra.execute(cql))
	group_mean_df = get_group_mean_result(cashflow_info)
	plot_data = generate_plot(group_mean_df, "Group daily average cash flows")
	return plot_data


def generate_interest_rate_plot(start_date, end_date):
	cql = f"""
			select * from interest_rate 
			where date >= {start_date} and date <= {end_date} allow filtering 
			"""
	interest_rates = list(cassandra.execute(cql))
	if not interest_rates:
		plot_data = generate_blank_plot()
		return plot_data
	interest_rates_df = pd.DataFrame(interest_rates)
	interest_rates_df['date'] = pd.to_datetime(interest_rates_df['date'], format="%Y%m%d")
	interest_rates_df = interest_rates_df.set_index('date', drop=True)
	plot_data = generate_rate_plot(interest_rates_df)
	return plot_data


def generate_advice(end_date):
	cql = f"""
			select fund_yield_rate, shibor_1_month, shibor_1_week, shibor_1_year from interest_rate
			where date = {end_date}
			"""
	interest_rates = cassandra.execute(cql)[0]
	return interest_rates

