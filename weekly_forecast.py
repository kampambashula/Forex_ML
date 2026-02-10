# -*- coding: utf-8 -*-
"""
Weekly Kwacha Forecast Script (Institutional Grade)
Generates:
1. Professional FX note
2. WhatsApp-friendly commentary
3. Short X/Twitter post

Features:
- Analysis-driven direction
- Hard-coded commentary language
- Confidence bands (model dispersion)
- Risk-on / Risk-off regime
- Volatility shock alerts
- Last-week comparison
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
LOOKBACK_WEEKS = 4

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

# ==============================
# DIRECTION
# ==============================
if change > 0:
    direction = "weakening"
elif change < 0:
    direction = "strengthening"
else:
    direction = "stable"

# ==============================
# HARD-CODED COMMENTARY
# ==============================
COMMENTARY = {
    "weakening": {
        "professional": "Our models suggest a modest weakening of the Kwacha over the week.",
        "conversational": "Looking ahead, the Kwacha is expected to soften slightly.",
        "short": "Models point to a slight weakening of the Kwacha this week."
    },
    "strengthening": {
        "professional": "Our models suggest a modest strengthening of the Kwacha over the week.",
        "conversational": "Looking ahead, the Kwacha is expected to firm slightly.",
        "short": "Models point to a slight strengthening of the Kwacha this week."
    },
    "stable": {
        "professional": "Our models suggest broadly stable Kwacha trading over the week.",
        "conversational": "Looking ahead, the Kwacha is expected to remain fairly stable.",
        "short": "Models point to broadly stable Kwacha trading this week."
    }
}

commentary = COMMENTARY[direction]

# ==============================
# CONFIDENCE BANDS
# ==============================
dispersion = (best_case - worst_case) / consensus * 100

if dispersion < 1.5:
    confidence_level = "high"
elif dispersion < 3.0:
    confidence_level = "moderate"
else:
    confidence_level = "low"

CONFIDENCE_LANGUAGE = {
    "high": "Confidence is high, with models tightly clustered.",
    "moderate": "Confidence is moderate, with some divergence across models.",
    "low": "Confidence is low, with wide variation across model outcomes."
}

confidence_commentary = CONFIDENCE_LANGUAGE[confidence_level]

# ==============================
# RISK REGIME
# ==============================
if direction == "strengthening" and confidence_level in ["high", "moderate"]:
    risk_regime = "risk-on"
elif direction == "weakening" and confidence_level == "low":
    risk_regime = "risk-off"
else:
    risk_regime = "neutral"

RISK_LANGUAGE = {
    "risk-on": "Market conditions suggest a risk-on environment, supportive of the Kwacha.",
    "risk-off": "Market conditions point to a risk-off environment, weighing on the Kwacha.",
    "neutral": "Market conditions remain mixed, with no clear risk bias."
}

risk_commentary = RISK_LANGUAGE[risk_regime]

# ==============================
# VOLATILITY SHOCK ALERT
# ==============================
range_pct = (best_case - worst_case) / current_rate * 100
abs_move_pct = abs(pct_change)

VOLATILITY_ALERTS = {
    "alert": "🚨 Volatility Alert: Models indicate elevated FX volatility with risk of sharp intraday moves.",
    "watch": "⚠️ Volatility Watch: Trading ranges have widened, warranting close monitoring.",
    "none": "No volatility shock signals detected."
}

if range_pct > 4.0 or abs_move_pct > 1.5:
    volatility_state = "alert"
elif range_pct > 2.5:
    volatility_state = "watch"
else:
    volatility_state = "none"

volatility_commentary = VOLATILITY_ALERTS[volatility_state]

# ==============================
# DATE LABEL
# ==============================
today = date.today()
week_label = f"{today:%d %b} – {(today + timedelta(days=6)):%d %b}"

# ==============================
# LAST WEEK & TREND SUMMARY
# ==============================
prev_files = sorted(OUTPUT_DIR.glob("weekly_post_professional_*.txt"))

if len(prev_files) >= 2:
    with open(prev_files[-2], "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'Consensus forecast: K([0-9.,]+)', content)
        last_week_consensus = float(match.group(1).replace(",", "")) if match else current_rate
else:
    last_week_consensus = current_rate

change_vs_last_week = consensus - last_week_consensus
pct_vs_last_week = (change_vs_last_week / last_week_consensus) * 100

recent_files = prev_files[-LOOKBACK_WEEKS:]
trend_values = []

for file in recent_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'Consensus forecast: K([0-9.,]+)', content)
        if match:
            trend_values.append(float(match.group(1).replace(",", "")))

if trend_values:
    trend_change = trend_values[0] - consensus 
    pct_trend = (trend_change / trend_values[0]) * 100
    trend_summary = (
        f"Over the past {len(trend_values)} week(s), the Kwacha has moved "
        f"{trend_change:+.2f} K ({pct_trend:+.2f}%)."
    )
else:
    trend_summary = ""

# ==============================
# SOCIAL POSTS
# ==============================

post_professional = f"""
🇿🇲 Kwacha Weekly Outlook
Week of {week_label}

{commentary["professional"]}

📊 Consensus forecast: K{consensus:,.2f} (vs last week: {change_vs_last_week:+.2f} ({pct_vs_last_week:+.2f}%))
📉 Expected trading range: K{worst_case:,.2f} – K{best_case:,.2f}
📈 Change vs current: {change:+.2f} ({pct_change:+.2f}%)

🔍 {confidence_commentary}
⚖️ {risk_commentary}
🚨 {volatility_commentary}

{trend_summary}

This outlook is based on a consensus of statistical and machine-learning models.
""".strip()

post_conversational = f"""
🇿🇲 Kwacha Weekly Outlook
{week_label}

{commentary["conversational"]}

📊 Consensus: K{consensus:,.2f}
📉 Range: K{worst_case:,.2f} – K{best_case:,.2f}

🔍 {confidence_commentary}
⚖️ {risk_commentary}
🚨 {volatility_commentary}

{trend_summary}
""".strip()

post_short = f"""
🇿🇲 Kwacha Outlook | {week_label}

{commentary["short"]}

📊 K{consensus:,.2f}
📉 Range: K{worst_case:,.2f} – K{best_case:,.2f}

⚠️ VOL: {volatility_state.upper()} | ⚖️ {risk_regime.upper()}
""".strip()

# ==============================
# SAVE OUTPUTS
# ==============================
output_prof = OUTPUT_DIR / f"weekly_post_professional_{today}.txt"
output_conv = OUTPUT_DIR / f"weekly_post_conversational_{today}.txt"
output_short = OUTPUT_DIR / f"weekly_post_short_{today}.txt"

for path, content in [
    (output_prof, post_professional),
    (output_conv, post_conversational),
    (output_short, post_short)
]:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ==============================
# CONSOLE OUTPUT
# ==============================
print("\n✅ Weekly Kwacha forecast generated successfully!\n")
print("Volatility State:", volatility_state.upper())
