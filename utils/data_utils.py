import pandas as pd

LAGS = [1, 5, 10, 20]
TARGET = "SELLING RATE"

def load_data(path):
    df = pd.read_csv(path)
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)
    return df

def create_lags(df):
    for lag in LAGS:
        df[f"lag_{lag}"] = df[TARGET].shift(lag)
    return df.dropna().reset_index(drop=True)
