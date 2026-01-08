import streamlit as st

st.title("About Kwacha Forex App")

# Full-width header image
st.image("assets/fx.png", use_container_width=True)

st.markdown("""
Welcome to the **Kwacha Forex App**, a professional tool for visualizing, forecasting,
and analyzing Zambian Kwacha foreign exchange rates.

This application is built using **historical Bank of Zambia FX data** and follows
**industry-standard time-series best practices**.

---

### Key Features

- **Lag-based Machine Learning Forecasts:** Uses Linear Regression, Random Forest, Decision Trees, and XGBoost models.
- **Recursive Forecasting:** Predictions are anchored to the most recent market data for realism.
- **Walk-Forward Backtesting:** Ensures validation is free from data leakage and simulates real-time forecasting.
- **Dynamic Visualizations:** Explore recent trends, moving averages, volatility, and multi-model forecasts.

---

### Designed For

- **Researchers & Economists:** Analyze trends and simulate policy scenarios.
- **Finance Professionals:** Evaluate FX behavior for decision support.
- **Students & Data Scientists:** Learn ML on real-world financial time-series data.

---

**Contact / Learn More:**

- GitHub: [Kampambashula](https://github.com/kampambashula)  
- Email: kampamba.shula@kampambashula.com

""")
