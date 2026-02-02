# -*- coding: utf-8 -*-
"""
Weekly Kwacha Forecast Script
Generates three ready-to-share social post formats:
1. Professional / Credible
2. Conversational / WhatsApp-friendly
3. Short & punchy / Twitter/X style
Includes:
- Last week comparison
- 4-week trend summary
"""

import numpy as np
from datetime import date, timedelta
from pathlib import Path
import re

from utils.data_utils import load_data, create_lags, LAGS, TARGET
from utils.ml_utils import get_models, recursive_forecast

# ==============================
# CONFIG
# ==============================
DATA_PATH = "data/data.csv"
OUTPUT_DIR = Path("outputs")
DAYS_TO_FORECAST = 7
LOOKBACK_WEEKS = 4  # For trend summary

OUTPUT_DIR.mkdir(exist_ok=True)

# ==============================
# LOAD & PREP DATA
# ==============================
df = create_lags(load_data(DATA_PATH))
feature_cols = [f"lag_{l}" for l in LAGS]

X = df[feature_cols]
y = df[TARGET]

last_row = df.iloc[-1]
current_rate = y.iloc[-1]

# ==============================
# RUN MODELS
# ==============================
forecasts = {}
for name, model in get_models().items():
    model.fit(X, y)
    forecasts[name] = recursive_forecast(
        model,
        last_row,
        feature_cols,
        DAYS_TO_FORECAST
    )

# ==============================
# END-OF-WEEK METRICS
# ==============================
eow_values = np.array([v[-1] for v in forecasts.values()])
consensus = eow_values.mean()
best_case = eow_values.max()
worst_case = eow_values.min()

change = consensus - current_rate
pct_change = (change / current_rate) * 100

if change > 0:
    outlook = "Kwacha is expected to weaken slightly this week."
elif change < 0:
    outlook = "Kwacha is expected to strengthen slightly this week."
else:
    outlook = "Kwacha is expected to remain broadly stable this week."

# ==============================
# DATE LABEL
# ==============================
today = date.today()
week_label = f"{today:%d %b} – {(today + timedelta(days=6)):%d %b}"

# ==============================
# LAST WEEK & TREND SUMMARY
# ==============================
# Get previous weekly posts
prev_files = sorted(OUTPUT_DIR.glob("weekly_post_professional_*.txt"))

# --- Last week
if len(prev_files) >= 2:
    last_week_file = prev_files[-2]
    with open(last_week_file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'Consensus.*?K([0-9.]+)', content)
        last_week_consensus = float(match.group(1)) if match else current_rate
else:
    last_week_consensus = current_rate

change_vs_last_week = last_week_consensus - consensus
pct_vs_last_week = (change_vs_last_week / last_week_consensus) * 100

# --- 4-week trend
recent_files = prev_files[-LOOKBACK_WEEKS:] if prev_files else []
trend_values = []
for file in recent_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'Consensus.*?K([0-9.]+)', content)
        if match:
            trend_values.append(float(match.group(1)))

if trend_values:
    trend_change = consensus - trend_values[0]  # compare to oldest in last 4 weeks
    pct_trend = (trend_change / trend_values[0]) * 100
    trend_summary = f"Over the past {len(trend_values)} week(s), the Kwacha has moved {trend_change:+.2f} K ({pct_trend:+.2f}%)."
else:
    trend_summary = ""

# ==============================
# SOCIAL POST FORMATS
# ==============================

# --- Format 1: Professional / Credible
post_professional = f"""
🇿🇲 Kwacha Weekly Outlook
Week of {week_label}

Our models suggest the Kwacha may **weaken slightly** over the week.

📊 Consensus forecast: K{consensus:,.2f} (Change vs last week: {change_vs_last_week:+.2f} ({pct_vs_last_week:+.2f}%))
📉 Expected trading range: K{worst_case:,.2f} – K{best_case:,.2f}
📈 Change vs current: {change:+.2f} ({pct_change:+.2f}%)

{trend_summary}

This outlook is based on a consensus of statistical and machine-learning models.
""".strip()

# --- Format 2: Conversational / WhatsApp-friendly
post_conversational = f"""
🇿🇲 Kwacha Weekly Outlook
{week_label}

Looking ahead to the week, the Kwacha is expected to **soften slightly**.

📊 Consensus rate: K{consensus:,.2f} (vs last week: {change_vs_last_week:+.2f} ({pct_vs_last_week:+.2f}%))
📉 Likely range: K{worst_case:,.2f} – K{best_case:,.2f}
📈 Movement vs current: {change:+.2f} ({pct_change:+.2f}%)

{trend_summary}

Overall, models point to a modest weakening rather than any sharp move.
""".strip()

# --- Format 3: Short & Punchy / Twitter/X
post_short = f"""
🇿🇲 Kwacha Outlook | {week_label}

Models point to a **slight weakening** of the Kwacha this week.

📊 Consensus: K{consensus:,.2f} (vs last week: {change_vs_last_week:+.2f} ({pct_vs_last_week:+.2f}%))
📉 Range: K{worst_case:,.2f} – K{best_case:,.2f}
📈 Change: {change:+.2f} ({pct_change:+.2f}%)

{trend_summary}
""".strip()

# ==============================
# SAVE OUTPUTS
# ==============================
output_prof = OUTPUT_DIR / f"weekly_post_professional_{today}.txt"
output_conv = OUTPUT_DIR / f"weekly_post_conversational_{today}.txt"
output_short = OUTPUT_DIR / f"weekly_post_short_{today}.txt"

for filepath, content in zip(
    [output_prof, output_conv, output_short],
    [post_professional, post_conversational, post_short]
):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ==============================
# PRINT TO CONSOLE
# ==============================
print("\n✅ Weekly forecast generated successfully!\n")

print("=== PROFESSIONAL ===")
print(post_professional)
print(f"\n📄 Saved to: {output_prof.resolve()}")

print("\n=== CONVERSATIONAL ===")
print(post_conversational)
print(f"\n📄 Saved to: {output_conv.resolve()}")

print("\n=== SHORT & PUNCHY ===")
print(post_short)
print(f"\n📄 Saved to: {output_short.resolve()}")
