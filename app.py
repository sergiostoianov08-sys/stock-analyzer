import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ta
import math

st.set_page_config(
    page_title="Stock Analyzer Pro",
    layout="wide"
)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def clean(x):

    if x is None:
        return None

    try:
        if np.isnan(x):
            return None
    except:
        pass

    try:
        return float(x)
    except:
        return None


def pct(x):

    if x is None:
        return None

    return x * 100


def show(x, p=False):

    if x is None:
        return "N/A"

    if p:
        return f"{x:.2f}%"

    return f"{x:.2f}"


def human(n):

    if n is None:
        return "N/A"

    if n > 1e12:
        return f"{n/1e12:.2f}T"

    if n > 1e9:
        return f"{n/1e9:.2f}B"

    if n > 1e6:
        return f"{n/1e6:.2f}M"

    return str(round(n))


# ---------------------------------------------------
# DCF
# ---------------------------------------------------

def dcf_model(
    fcf,
    shares,
    growth,
    discount,
    terminal,
    years
):

    if (
        fcf is None
        or shares is None
        or shares == 0
    ):
        return None

    growth /= 100
    discount /= 100
    terminal /= 100

    if discount <= terminal:
        return None

    pv = 0

    current_fcf = fcf

    for year in range(1, years + 1):

        current_fcf *= (1 + growth)

        pv += (
            current_fcf
            /
            ((1 + discount) ** year)
        )

    terminal_fcf = current_fcf * (
        1 + terminal
    )

    terminal_value = (
        terminal_fcf
        /
        (discount - terminal)
    )

    terminal_pv = (
        terminal_value
        /
        ((1 + discount) ** years)
    )

    total_value = pv + terminal_pv

    return total_value / shares


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("DCF Settings")

growth = st.sidebar.slider(
    "FCF Growth %",
    0.0, 20.0, 8.0
)

discount = st.sidebar.slider(
    "Discount Rate %",
    5.0, 20.0, 10.0
)

terminal = st.sidebar.slider(
    "Terminal Growth %",
    0.0, 5.0, 2.5
)

years = st.sidebar.slider(
    "Years",
    5, 15, 10
)

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------

st.title("📈 Stock Analyzer Pro")

ticker_input = st.text_input(
    "Ticker",
    value="MSFT"
).upper()

if ticker_input:

    try:

        ticker = yf.Ticker(
            ticker_input
        )

        info = ticker.info

        hist = ticker.history(
            period="2y",
            auto_adjust=True
        )

        if hist.empty:

            st.error(
                "No data found"
            )

            st.stop()

        # TECHNICAL

        hist["RSI"] = (
            ta.momentum
            .RSIIndicator(
                hist["Close"]
            )
            .rsi()
        )

        hist["SMA50"] = (
            hist["Close"]
            .rolling(50)
            .mean()
        )

        hist["SMA200"] = (
            hist["Close"]
            .rolling(200)
            .mean()
        )

        current_price = (
            hist["Close"]
            .iloc[-1]
        )

        current_rsi = (
            hist["RSI"]
            .dropna()
            .iloc[-1]
        )

        # FUNDAMENTALS

        pe = clean(
            info.get("trailingPE")
        )

        forward_pe = clean(
            info.get("forwardPE")
        )

        peg = clean(
            info.get("pegRatio")
        )

        ev_ebitda = clean(
            info.get(
                "enterpriseToEbitda"
            )
        )

        roe = pct(
            clean(
                info.get(
                    "returnOnEquity"
                )
            )
        )

        gross_margin = pct(
            clean(
                info.get(
                    "grossMargins"
                )
            )
        )

        debt = clean(
            info.get(
                "debtToEquity"
            )
        )

        market_cap = clean(
            info.get(
                "marketCap"
            )
        )

        revenue_growth = pct(
            clean(
                info.get(
                    "revenueGrowth"
                )
            )
        )

        earnings_growth = pct(
            clean(
                info.get(
                    "earningsGrowth"
                )
            )
        )

        fcf = clean(
            info.get(
                "freeCashflow"
            )
        )

        shares = clean(
            info.get(
                "sharesOutstanding"
            )
        )

        fcf_yield = None

        if (
            fcf
            and market_cap
        ):

            fcf_yield = (
                fcf /
                market_cap
            ) * 100

        # Buffett

        buffett = 0

        if roe and roe > 15:
            buffett += 1

        if gross_margin and gross_margin > 40:
            buffett += 1

        if debt and debt < 50:
            buffett += 1

        if revenue_growth and revenue_growth > 0:
    
