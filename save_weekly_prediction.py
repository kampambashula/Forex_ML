# -*- coding: utf-8 -*-
"""
Save weekly Kwacha predictions for later performance review.
"""

import pandas as pd
from datetime import date, timedelta
from pathlib import Path
import numpy as np

from utils.data_utils import load_data, create_lags, LAGS, TARGET
from utils.ml_utils import get_models, recursive_forecast

# -----------------------------
# CONFIG
# -----------------------------
DATA_PATH = "data/data.csv"
PREDICTIONS_FILE = Path("predictions/weekly_predictions.csv")
DAYS_TO_FORECAST = 7

PREDICTIONS_FILE.parent.mkdir(exist_ok=True)

# -----------------------------
# LOAD & PREP DATA
# -----------------------------
df = create_lags(load_data(DATA_PATH))
feature_cols = [f"lag_{l}" for l in LAGS]

X = df[feature_cols]
y = df[TARGET]
last_row = df.iloc[-1]

# -----------------------------
# RUN MODELS
# -----------------------------
models = get_models()
model_forecasts = {}

for name, model in models.items():
    model.fit(X, y)
    model_forecasts[name] = recursive_forecast(model, last_row, feature_cols, DAYS_TO_FORECAST)

# -----------------------------
# CONSENSUS & RANGE
# -----------------------------
eow_values = np.array([v[-1] for v in model_forecasts.values()])
consensus = eow_values.mean()
best_case = eow_values.max()
worst_case = eow_values.min()

# -----------------------------
# SAVE PREDICTIONS
# -----------------------------
today = date.today()
week_start = today
week_end = today + timedelta(days=6)

# Flatten predictions into a row per model
rows = []
for model_name, values in model_forecasts.items():
    rows.append({
        "week_start": week_start,
        "week_end": week_end,
        "model": model_name,
        "predicted_rate": values[-1],
        "consensus": consensus,
        "best_case": best_case,
        "worst_case": worst_case
    })

df_pred = pd.DataFrame(rows)

# Append to CSV
if PREDICTIONS_FILE.exists():
    df_pred.to_csv(PREDICTIONS_FILE, mode="a", header=False, index=False, encoding="utf-8")
else:
    df_pred.to_csv(PREDICTIONS_FILE, mode="w", header=True, index=False, encoding="utf-8")

print(f"✅ Weekly predictions saved to {PREDICTIONS_FILE.resolve()}")
