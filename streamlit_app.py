import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pyti.average_true_range as atr

# Function to download and process data
@st.cache(suppress_st_warning=True, show_spinner=False)
def get_stock_data(ticker):
    start_date = "2020-01-01"
    end_date = "2023-05-07"
    
    data = yf.download(ticker, start=start_date, end=end_date)
    
    data['ATR'] = atr.average_true_range(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    
    return data.iloc[-1]

# Preferred stock tickers
tickers = ['AAPL', 'GOOGL', 'MSFT']  # Replace with the list of preferred stock tickers

# Streamlit app
st.title("Preferred Stocks Analysis")

with st.spinner('Loading stock data...'):
    # Download and process data
    stock_data = pd.DataFrame()
    for i, ticker in enumerate(tickers):
        stock_data[ticker] = get_stock_data(ticker)

# Calculate correlations
correlations = stock_data.T.pct_change().corr()

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write(correlations)
