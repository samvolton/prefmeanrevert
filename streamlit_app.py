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

# Function to download and process data
@st.cache(suppress_st_warning=True, show_spinner=False)
def get_stock_data(ticker):
    start_date = "2020-01-01"
    end_date = "2023-05-07"
    
    data = yf.download(ticker, start=start_date, end=end_date)
    
    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    
    return data.iloc[[-1]]

# Preferred stock tickers 
tickers = ['AAPL', 'GOOGL', 'MSFT']  # Replace with the list of preferred stock tickers

# Streamlit app
st.title("Preferred Stocks Analysis")

with st.spinner('Loading stock data...'):
    # Download and process data
    stock_data = pd.concat([get_stock_data(ticker).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)

stock_data = stock_data.set_index('Ticker')

# Calculate correlations
correlations = stock_data.T.pct_change().dropna().corr()

# Filter stocks based on minimum trading volume
min_volume = st.sidebar.slider('Minimum trading volume', 0, 1000000, 500000)
stock_data = stock_data[stock_data['Volume'] > min_volume]

# Filter stocks based on significant Z-Score deviation
z_score_threshold = st.sidebar.slider('Z-Score threshold', 0.0, 3.0, 1.5)
significant_deviation = stock_data[stock_data['Z_Score'].abs() > z_score_threshold]

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write(correlations)

st.header("Significant Z-Score Deviations")
st.write(significant_deviation[['ATR', 'SMA', 'STD', 'Z_Score']].T)

# Top gainers and losers
stock_data['Price_Change'] = stock_data['Close'].pct_change()
top_gainers = stock_data.nlargest(5, 'Price_Change')
top_losers = stock_data.nsmallest(5, 'Price_Change')

st.header("Top Gainers")
st.write(top_gainers[['Close', 'Price_Change']])

st.header("Top Losers")
st.write(top_losers[['Close', 'Price_Change']])
