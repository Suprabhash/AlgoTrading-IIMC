import pandas as pd
import yfinance as yf
from datetime import datetime

def get_data(ticker, frequency):
    """
    :param ticker: Ticker as on Reuters. Investpy and yfinance tickers can be passed using the lookup dict in tickers.py
    :param frequency: Frequency of the data required. Currently supports daily and hourly. Pass "D" or "H"
    :return:  Returns the OHLCV dataframe indexed by datetime
    """
    if frequency=='H':
        interval = "1H"
    if frequency == 'D':
        interval = "1D"

    ticker_dataframe = yf.download(ticker, interval=interval, start="2009-01-01", end=str(datetime.now())[:10]).reset_index()
    if 'Date' in ticker_dataframe.columns:
        ticker_dataframe.rename(columns={'Date': 'Datetime'}, inplace=True)
    ticker_dataframe["Datetime"] = pd.to_datetime(ticker_dataframe["Datetime"])
    return ticker_dataframe