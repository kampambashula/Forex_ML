import streamlit as st
import pandas as pd
from utils.data_utils import load_data, create_lags, LAGS, TARGET
from utils.ml_utils import walk_forward_backtest

def main():
    st.title("Walk-Forward Backtest")

    # Load and prepare data
    df = load_data("data/data.csv")
    df = create_lags(df)  # ensures all lag columns exist

    # Select backtest window
    window = st.slider("Walk-forward window size (days)", 5, 30, 20)

    # Prepare feature columns safely
    feature_cols = [f"lag_{l}" for l in LAGS]
    missing_cols = [col for col in feature_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Missing lag columns detected: {missing_cols}. Creating them now.")
        df = create_lags(df)  # regenerate lags if missing

    # Run backtest
    try:
        results = walk_forward_backtest(df, window)
        st.success("Backtest complete!")
        st.dataframe(results)
    except KeyError as e:
        st.error(f"KeyError encountered: {e}. Check if lag columns exist and data is clean.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

main()
