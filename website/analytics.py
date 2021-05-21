from flask import Blueprint, render_template, request, session, redirect, flash
from . import mongo
from . import cassandra
from .analytics_aux import *
from .forecasting import *
from .load_data_utils import generate_plot, generate_dataframe, get_group_mean_result

analytics = Blueprint('analytics', __name__)


def get_report(customer_id, report_date):
    cql = f"""
        select * from analytics_report 
        where user_id = {customer_id} and report_date = {report_date};
        """
    data = cassandra.execute(cql)[0]
    return data


def get_customer(customer_name):
    data = mongo.db.customer.find_one({'name': customer_name}, {'_id': 0})
    return data


def get_customer_properties(customer_id, properties):
    filter_query = {'_id': 0}
    for p in properties:
        filter_query[p] = 1
    customer_properties = mongo.db.customer.find_one({'user_id': customer_id}, filter_query)
    return customer_properties


def match_customer(customer_id, customer_name):
    data = mongo.db.customer.find_one({'user_id': customer_id, 'name': customer_name})
    return data is not None


def dates_correct(report_date, ana_date1, ana_date2):
    ana_dates_check = ana_date1 < ana_date2
    report_date_check = report_date >= ana_date2
    return ana_dates_check and report_date_check


@analytics.route('/crud_analytics_report', methods=['POST', 'GET'])
def crud_analytics_report():
    if request.method == 'GET':
        return render_template("crud_analytics_report.html")
    # auth_username = session.get('auth_username', None) TODO: change back after merge
    auth_username = "test"

    btn_type = request.form.get("btn_type")
    if btn_type == "create":
        customer_id = int(request.form.get('customer_id'))
        customer_name = request.form.get('customer_name')

        if not match_customer(customer_id, customer_name):
            flash('Incorrect Customer ID or Name, try again.', category='error')

        report_date = int(request.form.get('date'))
        ana_date1 = int(request.form.get('date1'))
        ana_date2 = int(request.form.get('date2'))

        if not dates_correct(report_date, ana_date1, ana_date2):
            flash('Ending date should be after staring date, and the report should be created after the ending date',
                  category='error')

        num_future_days = int(request.form.get('num_future_date'))
        customer_properties = []
        city = request.form.get('properties_boxes_1')
        gender = request.form.get('properties_boxes_2')
        constellation = request.form.get('properties_boxes_3')
        for elem in [city, gender, constellation]:
            if elem:
                customer_properties.append(elem)
        session['customer_name'] = customer_name
        report_prime_key = {'user_id': customer_id,
                            'report_date': report_date}
        mongo.db.appUser.update({'username': auth_username}, {"$addToSet": {"reports": report_prime_key}})
        cql = f"""
            insert into analytics_report (user_id, report_date, end_date, num_fdays, property, start_date)
            values ({customer_id}, {report_date}, {ana_date2}, {num_future_days}, {set(customer_properties)}, {ana_date1})
            """
        cassandra.execute(cql)
    elif btn_type == "delete":
        customer_name = request.form.get('customer_name2')
        print(customer_name)
        customer = get_customer(customer_name)
        if customer is None:
            flash("Customer does not exist, try again.", category='error')
            return redirect("/crud_analytics_report")
        customer_id = customer['user_id']
        report_date = int(request.form.get('report_date'))

        report_info = get_report(customer_id, report_date)
        if report_info is None:
            flash("Such report does not exist.", category='error')
            return redirect("/crud_analytics_report")

        mongo.db.appUser.update({'username': auth_username},
                                {'$pull': {'reports': {'user_id': customer_id, 'report_date': report_date}}}
                                )
        cql = f"""
            delete from analytics_report 
            where user_id = {customer_id} and report_date = {report_date};
            """
        cassandra.execute(cql)

    return render_template("crud_analytics_report.html")


@analytics.route('/view_all_report_properties', methods=['POST', 'GET'])
def view_all_report_properties():
    if request.method == "POST":
        customer_name = request.form.get('customer_name1')
        customer = get_customer(customer_name)
        if customer is None:
            flash("Customer does not exist, try again.", category='error')
            return redirect("/crud_analytics_report")
        customer_id = customer['user_id']
        cql = f"""
            select * from analytics_report where user_id = {customer_id}
            """
        report_properties = list(cassandra.execute(cql))
        if not report_properties:
            flash("No report created yet.", category='error')
            return redirect("/crud_analytics_report")
        return render_template("view_all_report_properties.html", user_profile=customer,
                               report_properties=report_properties)


@analytics.route('/view_report', methods=['POST', 'GET'])
def view_report():
    if request.method == "POST":
        customer_name = request.form.get('customer_name2')
        customer = get_customer(customer_name)
        if customer is None:
            flash("Customer does not exist, try again.", category='error')
            return redirect("/crud_analytics_report")
        customer_id = customer['user_id']
        report_date = int(request.form.get('report_date'))

        report_info = get_report(customer_id, report_date)
        if report_info is None:
            flash("Incorrect name or date.", category='error')
            return redirect("/crud_analytics_report")

        start_date = report_info['start_date']
        end_date = report_info['end_date']
        num_fdays = report_info['num_fdays']
        analytics_customer_properties = report_info['property']
        customer_properties = get_customer_properties(customer_id, analytics_customer_properties)

        group_daily_average_cashflow_plot = generate_group_daily_average_cashflow_plot(
            customer_properties, start_date, end_date
        )
        customer_cashflow_forecast_plot, arima_order = generate_customer_cashflow_forecast_plot(
            customer_id, start_date, end_date,
            num_fdays
        )
        interest_rate_plot = generate_interest_rate_plot(start_date, end_date)
        advice = generate_advice(end_date)
        return render_template("view_report.html", group_plot=group_daily_average_cashflow_plot,
                               forecast_plot=customer_cashflow_forecast_plot, interest_rate_plot=interest_rate_plot,
                               name=customer_name, report_date=report_date,
                               start_date=start_date, end_date=end_date, customer_properties=customer_properties,
                               advice=advice)
    else:
        return redirect("/crud_analytics_report")
