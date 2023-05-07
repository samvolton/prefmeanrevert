import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np


# Other functions are the same as before

def find_optimal_portfolio(correlations, min_stocks=2, max_stocks=None):
    if max_stocks is None:
        max_stocks = len(correlations.columns)

    optimal_portfolio = []
    min_avg_corr = float('inf')

    for num_stocks in range(min_stocks, max_stocks + 1):
        least_correlated_stocks = find_least_correlated_stocks(correlations, num_stocks)
        avg_corr = correlations.loc[least_correlated_stocks, least_correlated_stocks].mean().mean()
        if avg_corr < min_avg_corr:
            min_avg_corr = avg_corr
            optimal_portfolio = least_correlated_stocks

    return optimal_portfolio


# Streamlit app
st.title("Preferred Stocks Analysis")

# The rest of the code remains the same

least_correlated_stocks = find_least_correlated_stocks(correlations, num_stocks_in_portfolio)
portfolio = stock_data.loc[least_correlated_stocks]

st.header("Stock Parameters")
st.write(stock_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)

st.header("Correlations")
st.dataframe(correlations.style.highlight_max(axis=1))

st.header("Optimal Portfolio")
optimal_portfolio = find_optimal_portfolio(correlations)
optimal_portfolio_data = stock_data.loc[optimal_portfolio]
st.write(optimal_portfolio_data[['ATR', 'SMA', 'STD', 'Z_Score']].T)
