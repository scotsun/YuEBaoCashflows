import numpy as np
import pandas as pd
import base64
from io import BytesIO
from matplotlib.figure import Figure


def generate_customer_dict(user_id, profile_tbl, cashflow_tbl):
    customer_dict = dict()
    customer_row = profile_tbl.loc[profile_tbl['user_id'] == user_id].iloc[0]
    customer_dict['user_id'] = int(customer_row['user_id'])
    customer_dict['sex'] = int(customer_row['sex'])
    customer_dict['city'] = customer_row['city']
    customer_dict['constellation'] = customer_row['constellation']

    cashflows = []
    num_records = cashflow_tbl.loc[cashflow_tbl['user_id'] == user_id].shape[0]
    for i in range(num_records):
        row = cashflow_tbl.loc[cashflow_tbl['user_id'] == user_id].iloc[i, :]
        cashflow = generate_cashflow_dict(row)
        cashflows.append(cashflow)

    customer_dict['cashflows'] = cashflows
    return customer_dict


def generate_cashflow_dict(row):
    cashflow_dict = dict()
    cashflow_dict['report_date'] = int(row['report_date'])
    # sub dict
    purchase = dict()
    purchase['purchase_bal_amt'] = int(row['purchase_bal_amt'])
    purchase['purchase_bank_amt'] = int(row['purchase_bank_amt'])
    purchase['revenue'] = int(row['share_amt'])

    balance = dict()
    balance['tBalance'] = int(row['tBalance'])
    balance['yBalance'] = int(row['yBalance'])

    redemption = dict()
    redemption['consumption'] = dict()
    consumption = redemption['consumption']
    consumption['category1'] = -1 if np.isnan(row['category1']) else int(row['category1'])
    consumption['category2'] = -1 if np.isnan(row['category2']) else int(row['category2'])
    consumption['category3'] = -1 if np.isnan(row['category3']) else int(row['category3'])
    consumption['category4'] = -1 if np.isnan(row['category4']) else int(row['category4'])

    redemption['transfer'] = dict()
    transfer = redemption['transfer']
    transfer['tftobal_amt'] = int(row['tftobal_amt'])
    transfer['tftocard_amt'] = int(row['tftocard_amt'])
    # assemble
    cashflow_dict['balance'] = balance
    cashflow_dict['purchase'] = purchase
    cashflow_dict['redemption'] = redemption
    return cashflow_dict


def generate_plot(df):
    plot = Figure()
    ax = plot.subplots()
    df.plot(ax=ax)
    ax.legend(['balance', 'daily inflow', 'daily output'])
    ax.set_xlabel('date')
    ax.set_ylabel('CNY (0.01)')
    buf = BytesIO()
    plot.savefig(buf, format='png')
    data = base64.b64encode(buf.getbuffer()).decode('ascii')
    return data


def get_group_mean_result(cashflow_info):
    cashflow_df = pd.DataFrame(cashflow_info)
    group_mean_result = cashflow_df.groupby('report_date').mean()
    group_mean_result = group_mean_result.set_index(pd.to_datetime(group_mean_result.index, format="%Y%m%d"))
    return group_mean_result


def generate_dataframe(cashflow_info):
    cashflow_df = pd.DataFrame(cashflow_info)
    cashflow_df['report_date'] = pd.to_datetime(cashflow_df['report_date'], format="%Y%m%d")
    output_df = cashflow_df.set_index('report_date', drop=True)
    return output_df
