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
tickers = ['BAC-PB', 'BAC-PE', 'BAC-PM', 'BAC-PN', 'BAC-PO', 'BAC-PP', 'BAC-PQ', 'BAC-PS', 'BANFP', 'BEP-PA', 'BEPH', 'BEPI', 'BFS-PD', 'BFS-PE', 'BHFAL', 'BHFAM', 'BHFAN', 'BHFAO', 'BHFAP', 'BHR-PD', 'BIP-PA', 'BIP-PB', 'BIPH', 'BIPI', 'BML-PG', 'BML-PH', 'BML-PJ', 'BML-PL', 'BNH', 'BNJ', 'BOH-PA', 'BPOPM', 'BPOPO', 'BPYPN', 'BPYPO', 'BPYPP', 'BW-PA', 'BWBBP', 'BWNB', 'BWSN', 'C-PJ', 'C-PK', 'C-PN']  # Replace with the list of preferred stock tickers

# Streamlit app
st.title("Preferred Stocks Analysis")

with st.spinner('Loading stock data...'):
    # Download and process data
    stock_data = pd.concat([get_stock_data(ticker).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)

stock_data = stock_data.set_index('Ticker')

# Calculate correlations
correlations = stock_data.T.pct_change().corr()

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write(correlations)
