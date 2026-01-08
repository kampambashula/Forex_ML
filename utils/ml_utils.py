import numpy as np
import pandas as pd
import streamlit as st

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from utils.data_utils import LAGS, TARGET, create_lags

def get_models():
    """
    Return dictionary of ML models used for forecasting.
    """
    return {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "XGBoost": XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
    }

def recursive_forecast(model, last_row, feature_cols, steps):
    """
    Perform recursive forecasting for a given number of steps.
    Dynamically handles lags based on feature_cols.
    """
    preds = []
    current = last_row.copy()

    for _ in range(steps):
        # Prepare input
        X = current[feature_cols].values.reshape(1, -1)
        pred = model.predict(X)[0]
        preds.append(pred)

        # Shift lag columns dynamically
        for i in reversed(range(1, len(LAGS))):
            current[f"lag_{LAGS[i]}"] = current[f"lag_{LAGS[i-1]}"]
        current[f"lag_{LAGS[0]}"] = pred

    return preds

@st.cache_data(show_spinner=False)
def walk_forward_backtest(df, window=20, start_size=250, max_steps=300):
    """
    Run walk-forward backtesting on the dataframe.
    Ensures lag columns exist, fits models, and predicts one step at a time.
    """
    # Ensure lag columns exist
    df = create_lags(df)

    feature_cols = [f"lag_{l}" for l in LAGS]
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        st.warning(f"Missing lag columns detected: {missing_cols}. Re-generating lags.")
        df = create_lags(df)

    models = get_models()
    results = []

    end = min(len(df), start_size + max_steps)
    progress = st.progress(0)
    total = end - start_size

    for step, i in enumerate(range(start_size, end)):
        train = df.iloc[:i]
        test = df.iloc[i]

        X_train = train[feature_cols]
        y_train = train[TARGET]

        X_test = test[feature_cols].values.reshape(1, -1)
        y_test = test[TARGET]

        for name, model in models.items():
            model.fit(X_train, y_train)
            pred = model.predict(X_test)[0]

            results.append({
                "Date": test["DATE"],
                "Model": name,
                "Actual": y_test,
                "Predicted": pred,
                "Error": pred - y_test,
                "Abs Error": abs(pred - y_test)
            })

        progress.progress((step + 1) / total)

    return pd.DataFrame(results)
