import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_atr(high, low, close, n=14):
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low - close.shift()).abs()

    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/n, adjust=False).mean()
    return atr

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_stock_data(ticker, start_date, end_date, window):
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        return None

    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=window).mean()
    data['STD'] = data['Close'].rolling(window=window).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    
    return data.iloc[[-1]]

tickers = ['MSFT', 'AAPL', 'META', 'GOOGL', 'AMD', 'AMZN']  # Replace with your 600 tickers

st.title("Preferred Stocks Analysis")

time_intervals = {
    '1 day': 1,
    '1 week': 7,
    '1 month': 30,
    '1 year': 365,
    '2 years': 730,
    '5 years': 1825
}

selected_interval = st.sidebar.selectbox('Select time interval', list(time_intervals.keys()))

end_date = "2023-05-07"
start_date = pd.to_datetime(end_date) - pd.DateOffset(days=time_intervals[selected_interval])
start_date = start_date.strftime("%Y-%m-%d")

window = max(1, time_intervals[selected_interval] // 3)

with st.spinner('Loading stock data...'):
    stock_data_list = [get_stock_data(ticker, start_date, end_date, window) for ticker in tickers]
    stock_data_list = [data.assign(Ticker=ticker) for data, ticker in zip(stock_data_list, tickers) if data is not None]
    stock_data = pd.concat(stock_data_list, ignore_index=True)

stock_data = stock_data.set_index('Ticker')

correlations = stock_data.pct_change().dropna().T.corr()

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write("<style>table {width: 100% !important;}</style>", unsafe_allow_html=True)
st.dataframe(correlations)

st.header("Significant Z-Score Deviations")
significant_deviation = stock_data[stock_data['Z_Score'].abs() > 1.5]
st.write(significant_deviation[['ATR', 'SMA', 'STD', 'Z_Score']].T)
