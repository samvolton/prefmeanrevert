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
tickers = ['AAIC-PB', 'AAIC-PC', 'AAIN', 'AAM-PA', 'AAM-PB', 'ABR-PD', 'ABR-PE', 'ABR-PF', 'ACGLN', 'ACGLO', 'ACR-PC', 'ACR-PD', 'AEFC', 'AEL-PA', 'AEL-PB', 'AFGB', 'AFGC', 'AFGD', 'AFGE', 'AFSIA', 'AFSIB', 'AFSIC', 'AFSIM', 'AFSIN', 'AFSIP', 'AGM-PC', 'AGM-PD', 'AGM-PE', 'AGM-PF', 'AGM-PG', 'AGNCL', 'AGNCM', 'AGNCN', 'AGNCO', 'AGNCP', 'AHH-PA', 'AHL-PC', 'AHL-PD', 'AHT-PD', 'AHT-PF', 'AHT-PG', 'AHT-PH', 'AHT-PI','AIC', 'AIG-PA', 'AIRTP', 'AIZN', 'AJXA', 'AL-PA', 'ALL-PB', 'ALL-PG', 'ALL-PH', 'ALL-PI', 'ALTG-PA', 'AMH-PG', 'AMH-PH', 'AQNA', 'AQNB', 'ARBKL', 'ARGD', 'ARGO-PA', 'ARR-PC', 'ASB-PE', 'ASB-PF', 'ATCO-PD', 'ATCO-PH', 'ATCO-PI',  'ATH-PA', 'ATH-PB', 'ATH-PC', 'ATH-PD', 'ATLCL', 'ATLCP', 'AUVIP', 'AXS-PE', 'BAC-PB', 'BAC-PE', 'BAC-PM', 'BAC-PN', 'BAC-PO', 'BAC-PP', 'BAC-PQ', 'BAC-PS', 'BANFP', 'BEP-PA', 'BEPH', 'BEPI', 'BFS-PD', 'BFS-PE', 'BHFAL', 'BHFAM', 'BHFAN', 'BHFAO', 'BHFAP', 'BHR-PD', 'BIP-PA', 'BIP-PB', 'BIPH', 'BIPI', 'BML-PG', 'BML-PH', 'BML-PJ', 'BML-PL', 'BNH', 'BNJ', 'BOH-PA', 'BPOPM', 'BPOPO', 'BPYPN', 'BPYPO', 'BPYPP', 'BW-PA', 'BWBBP', 'BWNB', 'BWSN', 'C-PJ', 'C-PK', 'C-PN', 'CADE-PA', 'CCLDP', 'CCNEP', 'CDR-PB', 'CDR-PC', 'CDZIP', 'CFG-PD', 'CFG-PE', 'CGABL', 'CHMI-PA', 'CHMI-PB', 'CHRB', 'CHSCL', 'CHSCM', 'CHSCN', 'CHSCO', 'CHSCP', 'CIM-PA', 'CIM-PB', 'CIM-PC', 'CIM-PD', 'CIO-PA', 'CLDT-PA', 'CMRE-PB', 'CMRE-PC', 'CMRE-PD', 'CMRE-PE', 'CMS-PC', 'CMSA', 'CMSC', 'CMSD', 'CNFRL', 'CNOBP', 'CODI-PA', 'CODI-PB', 'CODI-PC', 'COF-PI', 'COF-PJ', 'COF-PK', 'COF-PL', 'COMSP', 'CSR-PC', 'CSSEN', 'CSSEP', 'CTBB', 'CTDD', 'CTO-PA', 'CUBB', 'CUBI-PE', 'CUBI-PF', 'DBRG-PH', 'DBRG-PI', 'DBRG-PJ', 'DCOMP', 'DCP-PB', 'DCP-PC', 'DDT', 'DHCNI',  'DLNG-PA', 'DLNG-PB', 'DLR-PJ', 'DLR-PK', 'DLR-PL', 'DRH-PA', 'DSX-PB', 'DTB', 'DTG', 'DTW', 'DUK-PA', 'DUKB', 'DX-PC', 'EBBNF', 'ECC-PD', 'ECCC', 'ECCV', 'ECCW', 'ECCX', 'EFC-PA', 'EFC-PB', 'EFSCP', 'EICA', 'ELC', 'ENJ', 'ENO', 'EP-PC', 'EQH-PA', 'EQH-PC', 'ESGRO', 'ESGRP', 'ETI-P', 'FATBP', 'FBIOP', 'FBRT-PE', 'FCNCO', 'FCNCP', 'FCRX', 'FGBIP', 'FGFPP', 'FHN-PC', 'FHN-PD', 'FHN-PE', 'FHN-PF', 'FITBI', 'FITBO', 'FITBP', 'FNB-PE', 'FOSLL', 'FRC-PH', 'FRC-PI', 'FRC-PJ', 'FRC-PK', 'FRC-PM', 'FRC-PN', 'FRGAP', 'FRT-PC', 'FTAIN', 'FTAIO', 'FTAIP', 'FULTP', 'GAB-PG', 'GAB-PH', 'GAB-PK', 'GAINN', 'GAINZ', 'GDV-PK', 'GECCM', 'GECCN', 'GECCO', 'GEGGL', 'GGT-PE', 'GGT-PG', 'GLOG-PA', 'GLOP-PA', 'GLOP-PB', 'GLOP-PC', 'GLP-PA', 'GLP-PB', 'GMBLP', 'GMLPF', 'GMRE-PA', 'GNL-PA', 'GNL-PB', 'GNT-PA', 'GOODN', 'GOODO', 'GPJA', 'GPMT-PA', 'GRBK-PA', 'GREEL', 'GS-PA', 'GS-PC', 'GS-PD', 'GS-PJ', 'GS-PK', 'GSL-PB', 'GUT-PC', 'HAWEL', 'HAWEM', 'HAWEN', 'HAWLI', 'HAWLL', 'HAWLM', 'HAWLN', 'HBANL', 'HBANM', 'HBANP', 'HCXY', 'HFRO-PA', 'HIG-PG', 'HNNAZ', 'HOVNP', 'HPP-PC', 'HROWL', 'HT-PC', 'HT-PD', 'HT-PE', 'HTFB', 'HTFC', 'HTIA', 'HTIBP', 'HTLFP', 'HWCPZ', 'ICR-PA', 'IIPR-PA', 'IMBIL', 'IMPPP', 'INBKZ', 'INN-PE', 'INN-PF', 'IVR-PB', 'IVR-PC', 'JPM-PC', 'JPM-PD', 'JPM-PJ', 'JPM-PK', 'JPM-PL', 'JPM-PM', 'JSM', 'JXN-PA', 'KEY-PI', 'KEY-PJ', 'KEY-PK', 'KEY-PL', 'KIM-PL', 'KIM-PM', 'KKRS', 'KMPB', 'KREF-PA', 'KTBA', 'LANDM', 'LANDO', 'LBRDP', 'LFMDP', 'LFT-PA', 'LTSA', 'LTSF', 'LTSH', 'LTSK', 'LTSL', 'LXP-PC', 'MBINM', 'MBINN', 'MBINO', 'MBINP', 'MBNKP', 'MDRRP', 'MET-PA', 'MET-PE', 'MET-PF', 'METCL', 'MFA-PB', 'MFA-PC', 'MGR', 'MGRB', 'MGRD', 'MHLA', 'MHNC', 'MITT-PA', 'MITT-PB', 'MITT-PC', 'MNSBP', 'MS-PA', 'MS-PE', 'MS-PF', 'MS-PI', 'MS-PK', 'MS-PL', 'MS-PO', 'MS-PP', 'MSBIP', 'NCV-PA', 'NCZ-PA', 'NEWTL', 'NEWTZ', 'NI-PB', 'NLY-PF', 'NLY-PG', 'NLY-PI', 'NREF-PA', 'NRUC', 'NS-PA', 'NS-PB', 'NS-PC', 'NSA-PA', 'NSS', 'NTRSO', 'NXDT-PA', 'NYCB-PA', 'NYMTL', 'NYMTM', 'NYMTN', 'NYMTZ', 'OAK-PA', 'OAK-PB', 'OCCIN', 'OCCIO', 'OCFCP', 'OFSSH', 'ONBPP', 'OPINL', 'OPP-PB', 'OXLCL', 'OXLCM', 'OXLCN', 'OXLCO', 'OXLCP', 'OXLCZ', 'OXSQG', 'OXSQZ', 'OZKAP', 'PACWP', 'PEB-PF', 'PEB-PG', 'PEB-PH', 'PFH', 'PFXNZ', 'PMT-PA', 'PMT-PB', 'PMT-PC', 'PNFPP', 'POWWP', 'PRE-PJ', 'PRH', 'PRIF-PD', 'PRIF-PF', 'PRIF-PH', 'PRIF-PI', 'PRIF-PK', 'PRIF-PL', 'PRS', 'PSA-PF', 'PSA-PG', 'PSA-PH', 'PSA-PI', 'PSA-PJ', 'PSA-PK', 'PSA-PL', 'PSA-PM', 'PSA-PN', 'PSA-PO', 'PSA-PP',  'PSA-PR', 'PSA-PS', 'PSBXP', 'PSBYP', 'PSBZP', 'PSEC-PA', 'PXSAP', 'QVCC', 'QVCD', 'RC-PE', 'RCB', 'RCC', 'REXR-PB', 'RF-PB', 'RF-PC', 'RF-PE', 'RILYG', 'RILYK', 'RILYL', 'RILYM', 'RILYN', 'RILYO', 'RILYP', 'RILYT', 'RILYZ', 'RITM-PA', 'RITM-PB', 'RITM-PC', 'RITM-PD', 'RIV-PA',  'RLJ-PA', 'RMPL-P', 'RNR-PF', 'RNR-PG', 'RTLPO', 'RTLPP', 'RWAYL', 'RWAYZ', 'RZB', 'RZC', 'SACC', 'SAJ', 'SAT', 'SAY', 'SB-PC', 'SB-PD', 'SBBA', 'SCCB', 'SCCC', 'SCCD', 'SCCE', 'SCCF', 'SCCG', 'SCE-PG', 'SCE-PH', 'SCE-PJ', 'SCE-PK', 'SCE-PL', 'SCHW-PD', 'SCHW-PJ', 'SEAL-PA', 'SEAL-PB', 'SF-PB', 'SF-PC', 'SF-PD', 'SHO-PH', 'SHO-PI', 'SI-PA', 'SIGIP', 'SITC-PA', 'SLG-PI', 'SNCRL', 'SNV-PD', 'SNV-PE', 'SOCGP', 'SOHOB', 'SOHON', 'SOHOO', 'SOJC', 'SOJD', 'SOJE', 'SPLP-PA', 'SPNT-PB', 'SQFTP', 'SR-PA', 'SRC-PA', 'SREA', 'SSSSL', 'STAR-PD', 'STAR-PG', 'STAR-PI', 'STT-PD', 'STT-PG', 'SYF-PA', 'T-PA', 'T-PC', 'TANNI', 'TANNL', 'TANNZ', 'TBB', 'TBC', 'TCBIO', 'TDS-PV', 'TECTP', 'TELZ', 'TFC-PI', 'TFC-PO', 'TFC-PR', 'TFINP', 'TFSA', 'TGH-PA', 'TGH-PB', 'TNP-PD', 'TNP-PE', 'TNP-PF', 'TPTA', 'TRINL', 'TRTN-PA', 'TRTN-PB', 'TRTN-PC', 'TRTN-PD', 'TRTN-PE', 'TRTX-PC', 'TVC', 'TVE', 'TWO-PA', 'TWO-PB', 'TWO-PC', 'UBP-PH', 'UBP-PK', 'UCBIO', 'UMH-PD', 'USB-PH', 'USB-PP', 'USB-PQ', 'USB-PR', 'USB-PS', 'UZD', 'UZE', 'UZF', 'VIASP', 'VLYPO', 'VLYPP', 'VNO-PL', 'VNO-PM', 'VNO-PO', 'VOYA-PB', 'WAFDP', 'WAL-PA', 'WBS-PF', 'WCC-PA', 'WFC-PA', 'WFC-PC', 'WFC-PD', 'WFC-PQ', 'WFC-PR', 'WFC-PY', 'WFC-PZ', 'WRB-PE', 'WSBCP', 'WTFCM', 'WTFCP', 'XFLT-PA', 'XOMAO', 'XOMAP', 'YGYIP', 'ZIONL', 'ZIONO', 'ZIONP']

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
