import plotly.graph_objects as go
import pandas as pd

from utils.data_utils import TARGET

def plot_forecasts(df, forecasts, days):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["DATE"],
        y=df[TARGET],
        mode="lines",
        name="Actual"
    ))

    last_date = df["DATE"].iloc[-1]
    future_dates = pd.date_range(last_date, periods=days + 1, freq="D")[1:]

    for name, preds in forecasts.items():
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=preds,
            mode="lines",
            name=name,
            line=dict(dash="dash")
        ))

    fig.update_layout(
        title="FX Selling Rate Forecast",
        xaxis_title="Date",
        yaxis_title="Rate"
    )
    return fig

def plot_backtest_errors(bt_df):
    summary = bt_df.groupby("Model")["Abs Error"].mean().reset_index()

    fig = go.Figure(go.Bar(
        x=summary["Model"],
        y=summary["Abs Error"]
    ))

    fig.update_layout(
        title="Walk-Forward Mean Absolute Error",
        yaxis_title="MAE"
    )
    return fig
