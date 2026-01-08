import streamlit as st
import pandas as pd
from utils.data_utils import load_data, create_lags, LAGS, TARGET
from utils.ml_utils import get_models, recursive_forecast
from utils.plot_utils import plot_forecasts

def main():
    st.title("Forecasts")

    df = create_lags(load_data("data/data.csv"))
    feature_cols = [f"lag_{l}" for l in LAGS]

    days_to_forecast = st.slider("Days to forecast", 5, 60, 30)
    history_window = st.selectbox("Historical window (days)", [15,30,60,90], index=1)

    models = get_models()
    forecasts = {}

    X = df[feature_cols]
    y = df[TARGET]
    last_row = df.iloc[-1]

    for name, model in models.items():
        model.fit(X, y)
        forecasts[name] = recursive_forecast(model, last_row, feature_cols, days_to_forecast)

    recent_df = df.tail(history_window)

    st.plotly_chart(plot_forecasts(recent_df, forecasts, days_to_forecast), use_container_width=True)

    st.caption(f"Showing last {history_window} days of actual rates with {days_to_forecast}-day forecasts.")

main()
