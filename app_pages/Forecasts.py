import streamlit as st
import pandas as pd
import numpy as np
from utils.data_utils import load_data, create_lags, LAGS, TARGET
from utils.ml_utils import get_models, recursive_forecast
from utils.plot_utils import plot_forecasts

# -------------------------------
# Page config (MOBILE FIRST)
# -------------------------------
st.set_page_config(
    page_title="Kwacha Forecast",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("🇿🇲 Kwacha Exchange Rate Forecast")

    # -------------------------------
    # Controls (collapsed for mobile)
    # -------------------------------
    with st.expander("⚙️ Forecast Settings"):
        days_to_forecast = st.slider("Days to forecast", 5, 60, 30)
        history_window = st.selectbox(
            "Historical window (days)",
            [15, 30, 60, 90],
            index=1
        )

    # -------------------------------
    # Data & models
    # -------------------------------
    df = create_lags(load_data("data/data.csv"))
    feature_cols = [f"lag_{l}" for l in LAGS]

    X = df[feature_cols]
    y = df[TARGET]
    last_row = df.iloc[-1]
    current_rate = y.iloc[-1]

    models = get_models()
    forecasts = {}

    for name, model in models.items():
        model.fit(X, y)
        forecasts[name] = recursive_forecast(
            model,
            last_row,
            feature_cols,
            days_to_forecast
        )

    # -------------------------------
    # End-of-week calculations
    # -------------------------------
    week_day_index = min(6, days_to_forecast - 1)

    eow_predictions = {
        name: forecast[week_day_index]
        for name, forecast in forecasts.items()
    }

    values = np.array(list(eow_predictions.values()))

    consensus = values.mean()
    best_case = values.max()
    worst_case = values.min()

    change = consensus - current_rate
    pct_change = (change / current_rate) * 100

    # Color cue
    delta_color = "normal" if change == 0 else ("inverse" if change < 0 else "normal")

    # -------------------------------
    # 📊 TOP METRICS (MOST IMPORTANT)
    # -------------------------------
    st.subheader("📅 End-of-Week Outlook")

    c1, c2 = st.columns(2)

    c1.metric(
        "📊 Consensus Rate",
        f"{consensus:,.2f}",
        delta=f"{change:+.2f} ({pct_change:+.2f}%)",
        delta_color=delta_color
    )

    c2.metric(
        "📉 Expected Range",
        f"{worst_case:,.2f} – {best_case:,.2f}"
    )

    c3, c4 = st.columns(2)

    c3.metric("🔼 Best Case", f"{best_case:,.2f}")
    c4.metric("🔽 Worst Case", f"{worst_case:,.2f}")

    st.divider()

    # -------------------------------
    # 🧠 WEEKLY OUTLOOK (PLAIN ENGLISH)
    # -------------------------------
    if change > 0:
        outlook = "Kwacha is expected to weaken slightly this week."
    elif change < 0:
        outlook = "Kwacha is expected to strengthen slightly this week."
    else:
        outlook = "Kwacha is expected to remain broadly stable this week."

    st.subheader("🧠 Weekly Outlook")
    st.write(
        f"""
        **Summary:** {outlook}  
        Based on model consensus, the exchange rate is likely to trade
        between **{worst_case:,.2f}** and **{best_case:,.2f}** by week end.
        """
    )

    st.divider()

    # -------------------------------
    # 🤖 MODEL PREDICTIONS (STACKED)
    # -------------------------------
    st.subheader("🤖 Model Predictions")

    for name, value in eow_predictions.items():
        st.metric(label=name, value=f"{value:,.2f}")

    st.divider()

    # -------------------------------
    # 📲 WHATSAPP SHARE SUMMARY
    # -------------------------------
    st.subheader("📲 Share on WhatsApp")

    whatsapp_text = f"""
🇿🇲 *Kwacha End-of-Week Forecast*

📊 Consensus: *{consensus:,.2f}*
📉 Range: *{worst_case:,.2f} – {best_case:,.2f}*
📈 Change vs today: *{change:+.2f} ({pct_change:+.2f}%)*

🧠 Outlook:
{outlook}

_Source: Statistical & ML models_
    """.strip()

    st.text_area(
        "Copy & share:",
        whatsapp_text,
        height=220
    )

    st.caption("Tip: Long-press → Copy → Paste into WhatsApp")

    # -------------------------------
    # 📈 CHART (LAST, OPTIONAL)
    # -------------------------------
    st.subheader("📈 Trend & Forecast")

    recent_df = df.tail(history_window)
    st.plotly_chart(
        plot_forecasts(recent_df, forecasts, days_to_forecast),
        use_container_width=True
    )

    st.caption(
        "Numbers shown above are end-of-week predictions. "
        "Chart is for deeper inspection."
    )

main()
