from flask import Blueprint, render_template, request, session, redirect, flash
from . import mongo
from . import cassandra
from .forecasting import *
from .load_data_utils import generate_plot, generate_dataframe, get_group_mean_result

analytics = Blueprint('analytics', __name__)


def find_customer(customer_id, customer_name):
    data = mongo.db.customer.find_one({'user_id': customer_id, 'name': customer_name})
    return data is not None


def dates_correct(report_date, ana_date1, ana_date2):
    ana_dates_check = ana_date1 < ana_date2
    report_date_check = report_date >= ana_date2
    return ana_dates_check and report_date_check


@analytics.route('/create_analytics_report', methods=['POST', 'GET'])
def create_analytics_report():
    if request.method == 'GET':
        return render_template("create_analytics_report.html")

    customer_id = int(request.form.get('customer_id'))
    customer_name = request.form.get('customer_name')

    if not find_customer(customer_id, customer_name):
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
    report_dict = {'user_id': customer_id,
                   'report_date': report_date,
                   'start_date': ana_date1,
                   'end_date': ana_date2,
                   'num_fdays': num_future_days,
                   'property': customer_properties}

    cql = f"""
        insert into analytics_report (user_id, report_date, end_date, num_fdays, property, start_date)
        values ({customer_id}, {report_date}, {ana_date2}, {num_future_days}, {set(customer_properties)}, {ana_date1})
        """

    mongo.db.report.insert_one(report_dict)
    cassandra.execute(cql)
    return render_template("create_analytics_report.html")


@analytics.route('/view_report', methods=['POST', 'GET'])
def view_report():
    return render_template("view_report.html")
