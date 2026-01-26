# -*- coding: utf-8 -*-
"""
Review past weekly predictions vs actual observed rates.
"""

import pandas as pd
from datetime import date
from pathlib import Path

PREDICTIONS_FILE = Path("predictions/weekly_predictions.csv")
DATA_PATH = "data/data.csv"

# -----------------------------
# LOAD PAST PREDICTIONS
# -----------------------------
if not PREDICTIONS_FILE.exists():
    print("No predictions found.")
    exit()

df_pred = pd.read_csv(PREDICTIONS_FILE, parse_dates=["week_start", "week_end"])

# -----------------------------
# LOAD ACTUAL DATA
# -----------------------------
df_actual = pd.read_csv(DATA_PATH, parse_dates=["date"])
df_actual = df_actual.sort_values("date")

# -----------------------------
# MERGE LAST WEEK
# -----------------------------
# Example: Review last week
last_week_start = df_pred["week_start"].max()
last_week_end = last_week_start + pd.Timedelta(days=6)

df_last_week_pred = df_pred[df_pred["week_start"] == last_week_start]

# Get actual end-of-week rate
actual_row = df_actual[df_actual["date"] == last_week_end]
if actual_row.empty:
    print(f"No actual data for end of week {last_week_end}.")
    actual_rate = None
else:
    actual_rate = actual_row["rate"].values[0]

# -----------------------------
# ASSESS PERFORMANCE
# -----------------------------
print(f"\nWeekly Performance Review | {last_week_start.date()} – {last_week_end.date()}\n")
print(f"Actual end-of-week rate: {actual_rate}\n")

for _, row in df_last_week_pred.iterrows():
    pred = row["predicted_rate"]
    error = pred - actual_rate if actual_rate else None
    print(f"Model: {row['model']}")
    print(f"  Predicted: {pred:.2f} | Error: {error:+.2f}" if actual_rate else f"  Predicted: {pred:.2f}")
print(f"\nConsensus forecast: {df_last_week_pred['consensus'].iloc[0]:.2f}")
