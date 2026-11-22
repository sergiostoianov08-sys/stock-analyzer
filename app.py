import streamlit as st

st.title("Stock Analyzer Pro")

ticker = st.text_input(
    "Введите тикер",
    value="MSFT"
)

st.write(
    f"Выбран тикер: {ticker}"
)
