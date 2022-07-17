import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def get_data(ticker, frequency):
    """
    :param ticker: Ticker as on Reuters. Investpy and yfinance tickers can be passed using the lookup dict in tickers.py
    :param frequency: Frequency of the data required. Currently supports daily and hourly. Pass "D" or "H"
    :return:  Returns the OHLCV dataframe indexed by datetime
    """
    start = "2009-01-01"
    end=str(datetime.now())[:10]

    if frequency=='H':
        interval = "1H"
    if frequency == 'D':
        interval = "1D"
    if frequency.endswith("min"):
        interval = frequency[:-3]+"m"
        start = str(datetime.now()-timedelta(days=6))[:10]

    ticker_dataframe = yf.download(ticker, interval=interval, start=start, end=end).reset_index()
    if frequency.endswith("min"):
        ticker_dataframe.Datetime = ticker_dataframe.Datetime.dt.tz_localize(None)
    if 'Date' in ticker_dataframe.columns:
        ticker_dataframe.rename(columns={'Date': 'Datetime'}, inplace=True)
    ticker_dataframe["Datetime"] = pd.to_datetime(ticker_dataframe["Datetime"])
    return ticker_dataframe