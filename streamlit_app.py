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

start_date, end_date = '2020-01-01', '2023-05-07'
stock_data = pd.concat([get_stock_data(ticker, start_date, end_date).assign(Ticker=ticker) for ticker in tickers], ignore_index=True)
stock_data = stock_data.set_index('Ticker')

correlations = stock_data.T.pct_change().dropna().corr()

num_stocks_in_portfolio = st.sidebar.slider('Number of stocks in portfolio', 1, len(tickers), 5)

least_correlated_stocks = find_least_correlated_stocks(correlations, num_stocks_in_portfolio)
portfolio = stock_data.loc[least_correlated_stocks]

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.write(correlations.style.highlight_max(axis=1))

st.header("Significant Z-Score Deviations")
significant_deviation = stock_data[stock_data['Z_Score'].abs() > 1.5]
st.write(significant_deviation[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Portfolio Creator")

num_stocks_in_portfolio = st.sidebar.number_input('Number of stocks in portfolio', min_value=1, max_value=len(tickers), value=5, step=1)

correlations_filtered = correlations.copy()
np.fill_diagonal(correlations_filtered.values, 0)

for stock in stock_data.index:
    if stock not in least_correlated_stocks:
        correlations_filtered.drop(stock, axis=0, inplace=True)
        correlations_filtered.drop(stock, axis=1, inplace=True)

portfolio_tickers = least_correlated_stocks.copy()

for i in range(num_stocks_in_portfolio - len(least_correlated_stocks)):
    new_stock = correlations_filtered.sum().idxmin()
    correlations_filtered.drop(new_stock, axis=0, inplace=True)
    correlations_filtered.drop(new_stock, axis=1, inplace=True)
    portfolio_tickers.append(new_stock)

st.write("Portfolio tickers:", portfolio_tickers)

portfolio = stock_data.loc[portfolio_tickers]
st.write(portfolio)

st.header("Portfolio Statistics")
st.write("Mean Daily Return:", portfolio['Close'].pct_change().mean())
st.write("Standard Deviation of Daily Returns:", portfolio['Close'].pct_change().std())
st.write("Sharpe Ratio:", portfolio['Close'].pct_change().mean() / portfolio['Close'].pct_change().std())

