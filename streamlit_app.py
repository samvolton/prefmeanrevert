import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import talib
from itertools import combinations

# Function to download and process data
def get_stock_data(ticker):
    start_date = "2020-01-01"
    end_date = "2023-05-07"
    
    data = yf.download(ticker, start=start_date, end=end_date)
    
    data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    
    return data.iloc[-1]

# Function to calculate pairwise correlation
def pairwise_correlation(data, tickers):
    corr_data = data[tickers].pct_change().corr()
    return corr_data

# Preferred stock tickers
tickers = ['AAPL', 'GOOGL', 'MSFT']  # Replace with the list of preferred stock tickers

# Download and process data
stock_data = pd.DataFrame()
for ticker in tickers:
    stock_data[ticker] = get_stock_data(ticker)

# Calculate correlations
correlations = pairwise_correlation(stock_data, tickers)

# Streamlit app
st.title("Preferred Stocks Analysis")

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write(correlations)

# Uncomment the following lines to display a heatmap of correlations
# import seaborn as sns
# import matplotlib.pyplot as plt

# st.header("Correlation Heatmap")
# plt.figure(figsize=(10, 10))
# sns.heatmap(correlations, annot=True, cmap='coolwarm', linewidths=0.5, vmin=-1, vmax=1)
# st.pyplot(plt.gcf())
