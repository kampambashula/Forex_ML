import streamlit as st
from PIL import Image

def main():
    st.title("Kwacha Forex App - Home")
    image = Image.open("assets/fx.png")
    st.image(image, use_container_width=True)

    st.markdown("""
    Welcome to the **Kwacha Forex App**!  
    Explore visualizations, forecasts, and backtesting tools for Zambian Kwacha FX rates.

    Use the **sidebar** to navigate through different pages.
    """)

main()
