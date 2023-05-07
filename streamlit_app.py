import yfinance as yf
import numpy as np
import pandas as pd
import streamlit as st


# Define the ticker symbols of the preferred stocks you want to analyze
tickers = ['PFF', 'PGX', 'PSK', 'PFXF']

# Download historical price data for each stock
prices = yf.download(tickers, start='2018-01-01', end='2023-05-06', group_by='ticker')['Adj Close']

# Calculate the rolling mean and standard deviation
rolling_mean = prices.rolling(window=20).mean()
rolling_std = prices.rolling(window=20).std()

# Calculate the z-score for each stock price
z_scores = (prices - rolling_mean) / rolling_std

# Set the threshold for identifying mean-reverting stocks
threshold = 2.0

# Identify mean-reverting stocks
mean_reverting_stocks = []
for ticker in tickers:
    if z_scores[ticker][-1] > threshold:
        mean_reverting_stocks.append(ticker)

# Print the list of mean-reverting stocks
print("Mean-Reverting Stocks: ", mean_reverting_stocks)


def mean_reverting_stocks(tickers):
    # Download historical price data for each stock
    prices = yf.download(tickers, start='2018-01-01', end='2023-05-06', group_by='ticker')['Adj Close']

    # Calculate the rolling mean and standard deviation
    rolling_mean = prices.rolling(window=20).mean()
    rolling_std = prices.rolling(window=20).std()

    # Calculate the z-score for each stock price
    z_scores = (prices - rolling_mean) / rolling_std

    # Set the threshold for identifying mean-reverting stocks
    threshold = 2.0

    # Identify mean-reverting stocks
    mean_reverting_stocks = []
    for ticker in tickers:
        if z_scores[ticker][-1] > threshold:
            mean_reverting_stocks.append(ticker)

    # Return the list of mean-reverting stocks
    return mean_reverting_stocks

# Create a Streamlit web app
st.title('Mean-Reverting Stocks')
tickers = st.text_input('Enter preferred stock symbols separated by commas (e.g., PFF,PGX,PSK,PFXF):')
tickers = [ticker.strip() for ticker in tickers.split(',')]
if len(tickers) > 0:
    mean_reverting_stocks = mean_reverting_stocks(tickers)
    if len(mean_reverting_stocks) > 0:
        st.write('Mean-Reverting Stocks:')
        for stock in mean_reverting_stocks:
            st.write(stock)
    else:
        st.write('No mean-reverting stocks found.')
