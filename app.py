import streamlit as st
import importlib

# =========================
# PAGE CONFIG
st.set_page_config(page_title="Kwacha Forex App", layout="wide")

# =========================
# DEFAULT PAGE ROUTING
query_params = st.query_params
current_page = query_params.get("page", ["home"])[0]  # default to home

# =========================
# SIDEBAR NAVIGATION WITH ICONS
st.sidebar.title("Navigation")

# Define page options with icons (Unicode/Emoji)
page_options = [
    {"key": "home", "label": "Home", "icon": "🏠"},
    {"key": "forecasts", "label": "Forecasts", "icon": "📈"},
    {"key": "walk_forward", "label": "Walk-Forward Backtest", "icon": "🔄"},
    {"key": "about", "label": "About", "icon": "ℹ️"}
]

# Build sidebar radio labels with icons
radio_labels = [
    f"{p['icon']} {p['label']}" for p in page_options
]

# Determine index of current active page
current_index = next(
    (i for i, p in enumerate(page_options) if p["key"] == current_page),
    0
)

# Display sidebar radio
selected_label = st.sidebar.radio("Go to", radio_labels, index=current_index)

# Update current_page based on selection
for p in page_options:
    if f"{p['icon']} {p['label']}" == selected_label:
        current_page = p["key"]
        st.query_params["page"] = [current_page]  # Update URL
        break

# =========================
# DYNAMIC PAGE IMPORT
page_module_mapping = {
    "home": "app_pages.Home",
    "forecasts": "app_pages.Forecasts",
    "walk_forward": "app_pages.Walk_Forward",
    "about": "app_pages.About"
}

module_name = page_module_mapping[current_page]
page_module = importlib.import_module(module_name)
