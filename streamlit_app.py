import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


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
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)

    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']

    return data.iloc[[-1]]


def find_least_correlated_stocks(correlations, num_stocks):
    selected_stocks = []
    remaining_stocks = correlations.columns.tolist()

    while len(selected_stocks) < num_stocks and len(remaining_stocks) > 0:
        if not selected_stocks:
            stock = remaining_stocks.pop(0)
            selected_stocks.append(stock)
        else:
            min_corr = float('inf')
            least_correlated_stock = None

            for stock in remaining_stocks:
                max_corr = correlations.loc[selected_stocks, stock].abs().max()
                if max_corr < min_corr:
                    min_corr = max_corr
                    least_correlated_stock = stock

            remaining_stocks.remove(least_correlated_stock)
            selected_stocks.append(least_correlated_stock)

    return selected_stocks


# Preferred stock tickers
tickers = ['MSFT', 'AAPL', 'META', 'GOOGL', 'AMD', 'AMZN']

# Streamlit app
st.title("Preferred Stocks Analysis")

time_intervals = {
    '1 Week': '7d',
    '10 Days': '10d',
    '1 Month': '1mo',
    '1 Year': '1y',
    '2 Years': '2y',
    '5 Years': '5y',
}

selected_interval = st.sidebar.selectbox('Time interval for correlations', list(time_intervals.keys()))

end_date = datetime.today()
start_date = end_date - pd.to_timedelta(time_intervals[selected_interval])

stock_data = pd.concat([get_stock_data(ticker, start_date, end_date).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)
stock_data = stock_data.set_index('Ticker')

correlations = stock_data.T.pct_change().dropna().corr()

num_stocks_in_portfolio = st.sidebar.slider('Number of stocks in portfolio', 1, len(tickers), 5)

least_correlated_stocks = find_least_correlated_stocks(correlations, num_stocks_in_portfolio)
portfolio = stock_data.loc[least_correlated_stocks]

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.dataframe(correlations.style.highlight_max(axis=1))

st.header("Portfolio")

st.header("Portfolio")
st.write(portfolio[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Significant Z-Score Deviations")
significant_z_score_deviations = stock_data[(stock_data['Z_Score'] > 2) | (stock_data['Z_Score'] < -2)]
st.write(significant_z_score_deviations[['Z_Score']].T)
