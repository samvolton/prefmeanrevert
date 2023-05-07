import yfinance as yf
import numpy as np
import pandas as pd
import streamlit as st

@st.cache
def download_data(tickers):
    # Download historical price data for each stock
    prices = yf.download(tickers, start='2022-02-01', end='2023-05-05')['Adj Close']
    return prices

def calculate_z_scores(prices):
    # Calculate the rolling mean and standard deviation
    rolling_mean = prices.rolling(window=20).mean()
    rolling_std = prices.rolling(window=20).std()

    # Calculate the z-score for each stock price
    z_scores = (prices - rolling_mean) / rolling_std
    return z_scores

def identify_mean_reverting_stocks(tickers, z_scores):
    # Set the threshold for identifying mean-reverting stocks
    threshold = 2.0

    # Identify mean-reverting stocks
    mean_reverting_stocks = []
    for ticker in tickers:
        if z_scores[ticker][-1] > threshold:
            mean_reverting_stocks.append(ticker)

    # Return the list of mean-reverting stocks
    return mean_reverting_stocks

# Define the ticker symbols of the preferred stocks you want to analyze
tickers = ['BAC-PB', 'BAC-PE', 'BAC-PM', 'BAC-PN', 'BAC-PO', 'BAC-PP', 'BAC-PQ', 'BAC-PS', 'BANFP', 'BEP-PA', 'BEPH', 'BEPI', 'BFS-PD', 'BFS-PE', 'BHFAL', 'BHFAM', 'BHFAN', 'BHFAO', 'BHFAP', 'BHR-PD', 'BIP-PA', 'BIP-PB', 'BIPH', 'BIPI', 'BML-PG', 'BML-PH', 'BML-PJ', 'BML-PL', 'BNH', 'BNJ', 'BOH-PA', 'BPOPM', 'BPOPO', 'BPYPN', 'BPYPO', 'BPYPP', 'BW-PA', 'BWBBP', 'BWNB', 'BWSN', 'C-PJ', 'C-PK', 'C-PN']

# Download historical price data for each stock
prices = download_data(tickers)

# Calculate the z-score for each stock price
z_scores = calculate_z_scores(prices)

# Identify mean-reverting stocks
mean_reverting_stocks = identify_mean_reverting_stocks(tickers, z_scores)

# Create a Streamlit web app
st.title('Mean-Reverting Stocks')
st.write('Historical price data from 2022-02-01 to 2023-05-05')
st.write(prices)
if len(mean_reverting_stocks) > 0:
    st.write('Mean-Reverting Stocks:')
    for stock in mean_reverting_stocks:
        st.write(stock)
else:
    st.write('No mean-reverting stocks found.')
