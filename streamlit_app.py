import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Function to calculate ATR
def calculate_atr(high, low, close, n=14):
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low - close.shift()).abs()

    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    return atr

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    return data.iloc[[-1]]

def get_stock_correlations(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

tickers = ['MSFT', 'AAPL', 'META', 'GOOGL', 'AMD', 'AMZN']

st.title("Preferred Stocks Analysis")

date_ranges = {
    '1 Week': ('2023-04-30', '2023-05-07'),
    '10 Days': ('2023-04-27', '2023-05-07'),
    '1 Month': ('2023-04-07', '2023-05-07'),
    '1 Year': ('2022-05-07', '2023-05-07'),
    '2 Years': ('2021-05-07', '2023-05-07'),
    '5 Years': ('2018-05-07', '2023-05-07'),
}

selected_date_range = st.sidebar.selectbox('Select time interval for correlations', list(date_ranges.keys()))

start_date, end_date = date_ranges[selected_date_range]

stock_data = pd.concat([get_stock_data(ticker, start_date, end_date).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)
stock_data = stock_data.set_index('Ticker')

correlation_data = pd.concat([get_stock_correlations(ticker, start_date, end_date).rename(ticker) for ticker in tickers], axis=1)
correlations = correlation_data.pct_change().dropna().corr()

min_volume = st.sidebar.slider('Minimum trading volume', 0, 1000000, 
