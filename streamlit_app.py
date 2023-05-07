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

tickers = ['MSFT', 'AAPL', 'META', 'GOOGL', 'AMD', 'AMZN']

st.title("Preferred Stocks Analysis")

# Time intervals
time_intervals = {
    '1 week': 7,
    '10 days': 10,
    '1 month': 30,
    '1 year': 365,
    '2 years': 730,
    '5 years': 1825
}

selected_interval = st.sidebar.selectbox('Select time interval', list(time_intervals.keys()))

end_date = "2023-05-07"
start_date = pd.to_datetime(end_date) - pd.DateOffset(days=time_intervals[selected_interval])
start_date = start_date.strftime("%Y-%m-%d")

with st.spinner('Loading stock data...'):
    stock_data = pd.concat([get_stock_data(ticker, start_date, end_date).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)

stock_data = stock_data.set_index('Ticker')

correlations = stock_data.T.pct_change().dropna().corr()

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.dataframe(correlations.style.highlight_max(axis=1))

st.header("Significant Z-Score Deviations")
significant_deviation = stock_data[stock_data['Z_Score'].abs() > 1.5]
st.write(significant_deviation[['ATR', 'SMA', 'STD', 'Z_Score']].T)
