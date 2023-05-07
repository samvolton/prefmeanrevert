import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def calculate_atr(high, low, close, n):
    tr1 = abs(high - low)
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    return atr

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if data.empty:
        return data.assign(Ticker=ticker)
    
    data['ATR'] = calculate_atr(data['High'], data['Low'], data['Close'], 14)
    data['SMA'] = data['Close'].rolling(window=10).mean()
    data['STD'] = data['Close'].rolling(window=10).std()
    data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
    
    return data.iloc[[-1]].assign(Ticker=ticker)

st.title('Mean Reverting Stocks')

tickers = st.text_input('Enter your stock tickers (comma-separated)').split(',')

start_date = (datetime.today() - timedelta(days=365 * 5)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

stock_data = pd.concat([get_stock_data(ticker.strip(), start_date, end_date).assign(Ticker=ticker.strip()) for ticker in tickers], ignore_index=True)

if not stock_data.empty:
    stock_data = stock_data.set_index('Ticker')
    st.write(stock_data)

    st.subheader('Stock Correlations')
    corr_periods = {
        '1 Week': 5,
        '10 Days': 10,
        '1 Month': 21,
        '3 Months': 63,
        '6 Months': 126,
        '1 Year': 252,
        '2 Years': 504,
        '5 Years': 1260
    }

    selected_period = st.selectbox('Select correlation period', list(corr_periods.keys()))

    correlations = stock_data.corr().iloc[:,-1 * corr_periods[selected_period]:]
    st.dataframe(correlations.style.highlight_max(axis=1).set_table_styles([{'selector': 'th', 'props': [('width', '100px')]}]))

    st.subheader('Portfolio Builder')
    target_corr = st.slider('Target Correlation', -1.0, 1.0, -0.3, 0.1)
    selected_stocks = correlations[(correlations < target_corr)].dropna(how='all').index.tolist()
    st.write(f'Stocks with a correlation lower than {target_corr}: {", ".join(selected_stocks)}')
else:
    st.write('No data available for the entered tickers.')
