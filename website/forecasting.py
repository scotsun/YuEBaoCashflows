import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pmdarima as pm
from datetime import timedelta
from matplotlib.figure import Figure
from io import BytesIO
import base64


def get_acf_plot(cashflows_df_column):
    acf_plot = Figure()
    ax = acf_plot.subplots()
    pm.utils.plot_acf(cashflows_df_column, ax=ax)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Correlation')
    buf = BytesIO()
    acf_plot.savefig(buf, format='png')
    acf_plot_output_data = base64.b64encode(buf.getbuffer()).decode('ascii')
    return acf_plot_output_data


def get_pacf_plot(cashflows_df_column):
    pacf_plot = Figure()
    ax = pacf_plot.subplots()
    pm.utils.plot_pacf(cashflows_df_column, ax=ax)
    ax.set_xlabel('Lag')
    ax.set_ylabel('Partial Correlation')
    buf = BytesIO()
    pacf_plot.savefig(buf, format='png')
    pacf_plot_output_data = base64.b64encode(buf.getbuffer()).decode('ascii')
    return pacf_plot_output_data


def auto_arima_forecasting(cashflows_df_column, num_future_dates, title):
    arima_model = pm.auto_arima(cashflows_df_column, seasonal=False)
    arima_order = arima_model.get_params()['order']
    forecasts = arima_model.predict(n_periods=num_future_dates)

    last_train_date = cashflows_df_column.index[-1]
    future_dates = [last_train_date + timedelta(days=i) for i in range(1, 1 + num_future_dates)]

    output_plot = Figure()
    output_plot_ax = output_plot.subplots()
    output_plot_ax.plot(cashflows_df_column.index, cashflows_df_column.values, c='b', label="past data")
    output_plot_ax.plot(future_dates, forecasts, c='orange', label="forecasted data")
    output_plot_ax.set_title(f"Forecasting future {num_future_dates} days' {title} data")
    output_plot_ax.legend(loc="best")
    buf = BytesIO()
    output_plot.savefig(buf, format='png')
    output_plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')

    return output_plot_data, arima_order
