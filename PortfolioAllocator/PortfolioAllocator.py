import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (15,5)
plt.rcParams['axes.grid'] = False
import seaborn as sns
sns.set_style("whitegrid", {'axes.grid' : False})
from Strategies.MA_Momentum.MA_Momentum import MA_Momentum
from Metrics.Metrics import SharpeRatio
import sys
import os
sys.path.append(os.getcwd())
import numpy as np
import pandas as pd
import os
from Utils.utils import interpret_time_unit, valid_dates

class PortfolioAllocator:
    def __init__(self, df):
        self.data = df

    def create_dates(self, time_unit):
        if time_unit=="all":
            self.dates = valid_dates(pd.date_range(start=str(self.data.iloc[0]['Datetime']), end="2040-06-15", freq=f'{(pd.to_datetime(self.data.iloc[-1]["Datetime"])-pd.to_datetime(self.data.iloc[0]["Datetime"])).days}D'))
        else:
            self.time_unit = interpret_time_unit(time_unit)
            self.dates = valid_dates(pd.date_range(start=str(self.data.iloc[0]['Datetime']), end="2036-06-15", freq=f'{self.time_unit[0]}{self.time_unit[1]}'))

    def select_tickers(self, tickers):
        self.selected_tickers = []
        for date in self.dates:
            self.selected_tickers.append(tickers)

    def allocate(self, initial_portfolio_value, interest_rate):

        current_balance = initial_portfolio_value
        equity_allocation = 0
        cash_allocation = 0
        portfolio_value = pd.DataFrame()

        for date_i, date, in enumerate(self.dates):
            start_date = date
            end_date = self.dates[date_i+1]
            df = self.data[(self.data["Datetime"]>=str(start_date)[:10])&(self.data["Datetime"]<str(end_date)[:10])]
            tickers = self.selected_tickers[date_i]

            for ticker in tickers:
                df[f"{ticker}_Signal"].fillna(0, inplace=True)
                df[f"{ticker}_SignalFfillPrice"] = df[f"{ticker}_Signal"].shift(1)
                df[f"{ticker}_SignalFfillPrice"].iloc[0] = 1
                for k in range(len(df[f"{ticker}_SignalFfillPrice"])):
                    if ((df["Equity_Signal"].iloc[k] == 1) & (df["Equity_Signal"].shift(1).fillna(0).iloc[k] == 0)):
                        df[f"{ticker}_SignalFfillPrice"].iloc[k] = 1
                df[f"{ticker}_SignalFfillPrice"] = df[f"{ticker}_Close"] * df[f"{ticker}_SignalFfillPrice"].replace(0, np.nan)
                df[f"{ticker}_SignalFfillPrice"].fillna(method="ffill", inplace=True)

            percent_tracker_current_balance_ticker = {}
            percent_tracker_units_ticker = {}
            percent_ticker = {}
            for ticker in tickers:
                percent_tracker_current_balance_ticker[ticker] = current_balance / len(tickers)
                percent_tracker_units_ticker[ticker] = percent_tracker_current_balance_ticker[ticker] / df.iloc[0][f"{ticker}_Close"]

            current_balance_ticker = {}
            units_ticker = {}
            for ticker in tickers:
                current_balance_ticker[ticker] = current_balance / len(tickers)
                units_ticker[ticker] = current_balance_ticker[ticker] / df.iloc[0][f"{ticker}_Close"]

            for i in range(len(df)):
                num_act_tickers = 0
                unallocated = 0
                for ticker in tickers:
                    if (df[f"{ticker}_Signal"].iloc[i] == 1):
                        num_act_tickers = num_act_tickers + 1
                    percent_tracker_current_balance_ticker[ticker] = percent_tracker_units_ticker[ticker] * df.iloc[i][f"{ticker}_Close"]
                for ticker in tickers:
                    percent_ticker[ticker] = percent_tracker_current_balance_ticker[ticker] / sum(percent_tracker_current_balance_ticker.values())

                signal_equity = df["Equity_Signal"].iloc[i]

                if signal_equity == 1:
                    nifty_allocation = current_balance
                    cash_allocation = 0
                if signal_equity == 0:
                    nifty_allocation = 0
                    cash_allocation = current_balance

                if ((df["Equity_Signal"].iloc[i] == 1) & (df["Equity_Signal"].shift(1).fillna(0).iloc[i] == 0)):
                    for ticker in tickers:
                        current_balance_ticker[ticker] = nifty_allocation * percent_ticker[ticker]
                        units_ticker[ticker] = current_balance_ticker[ticker] / df.iloc[i][f"{ticker}_Close"]

                if ((df["Equity_Signal"].iloc[i] == 0) & (df["Equity_Signal"].shift(1).fillna(1).iloc[i] == 1)):
                    for ticker in tickers:
                        current_balance_ticker[ticker] = 0
                        units_ticker[ticker] = 0

                if signal_equity == 1:
                    nifty_allocation = 0
                    for ticker in tickers:
                        if (df[f"{ticker}_Signal"].iloc[i] == 1):
                            current_balance_ticker[ticker] = units_ticker[ticker] * df.iloc[i][f"{ticker}_Close"]
                        else:
                            current_balance_ticker[ticker] = 0
                            unallocated = unallocated + units_ticker[ticker] * df.iloc[i][f"{ticker}_SignalFfillPrice"]
                        nifty_allocation = nifty_allocation + current_balance_ticker[ticker]


                unallocated = unallocated * (1 + interest_rate / 25200)
                cash_allocation = cash_allocation * (1 + interest_rate / 25200)
                current_balance = nifty_allocation + cash_allocation + unallocated
                portfolio_day = {'Datetime': df.iloc[i]["Datetime"], 'Equity_Signal': signal_equity, 'nifty_allocation': nifty_allocation,
                                 'cash_allocation': cash_allocation, 'Pvalue': current_balance, 'unallocated': unallocated, "Number of Active Tickers": num_act_tickers}
                for ticker in tickers:
                    portfolio_day[f"{ticker}_Close"] = df.iloc[i][f"{ticker}_Close"]
                    portfolio_day[f"{ticker}_Signal"] = df.iloc[i][f"{ticker}_Signal"]
                    portfolio_day[f"{ticker}_Percent"] = percent_ticker[ticker]
                    portfolio_day[f"{ticker}_Units"] = units_ticker[ticker]
                    portfolio_day[f"{ticker}_Current_Balance"] = current_balance_ticker[ticker]
                portfolio_day = pd.DataFrame([portfolio_day])
                portfolio_day = portfolio_day.set_index("Datetime")
                portfolio_value = pd.concat([portfolio_value, portfolio_day], axis=0, join="outer")

            if date_i==len(self.dates)-2:
                break

        return portfolio_value, units_ticker


        