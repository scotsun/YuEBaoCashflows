import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pmdarima as pm
from pmdarima.model_selection import train_test_split
from datetime import timedelta

from matplotlib.figure import Figure
from io import BytesIO
import base64

from load_data_utils import generate_dataframe


def auto_arima_forecasting(cashflows, num_future_dates):
    cashflows_df = generate_dataframe(cashflows) # TODO: only balance now
    arima_model = pm.auto_arima(cashflows_df, seasonal=False)
    forecasts = arima_model.predict(num_future_dates)

    last_train_date = cashflows_df.index[-1]
    future_dates = [last_train_date + timedelta(days=i) for i in range(1, 1 + num_future_dates)]

    output_plot = Figure()
    output_plot_ax = output_plot.subplots()
    output_plot_ax.plot(cashflows_df.index, cashflows_df['balance'].values, c='blue')
    output_plot_ax.plot(future_dates, forecasts, c='orange')
    buf = BytesIO()
    output_plot.savefig(buf, format='png')
    output_plot_data = base64.b64encode(buf.getbuffer()).decode('ascii')

    return output_plot_data



