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

import pandas as pd
from PortfolioAllocator.PortfolioAllocator import PortfolioAllocator
from BacktestOptimiser.BacktestOptimiser import BacktestOptimiser
from Utils.utils import correlation_filter
from StockScreener.screener import screener
from StockScreener.Nifty50 import tickers as universe_of_stocks
from StockScreener.screener import simple_momentum_rules as rules

if __name__=='__main__':

    print("Selecting Tickers")
    universe_of_stocks = universe_of_stocks[:10]
    sc = screener(universe_of_stocks=universe_of_stocks, screener_rules=rules)
    tickers = sc.select_tickers(number=10)
    print(f"Tickers selected: {tickers}")

    for ticker in tickers:
        print(f"Processing {ticker}")
        optimiser = BacktestOptimiser(strategy = MA_Momentum, ticker = ticker, data_frequency = 'D')

        print("Getting data")
        optimiser.get_data()

        print("Creating Dates")
        optimiser.create_dates("12_Months")

        print("Adding features")
        optimiser.add_features()

        print("run_backtests"),
        optimiser.run_backtests(use_optimiser="BruteForce",parallelize=False)

        print("Selecting Strategies")
        optimiser.select_strategies(use_optimiser = "BruteForce",parallelize=False)

        # print("Checking Selected Strategies")
        # optimiser.check_selected_strategies(forward_time={"months": 2})

        print("Filtering Strategies")
        optimiser.filter_strategies(filter_function = correlation_filter)

        print("Optimizing weights")
        optimiser.optimize_weights()

        print("Selecting best and mailing results")
        optimiser.select_best_and_mail_results(parallelize=False)

    print("Gathering Results")
    df = pd.DataFrame()
    for ticker in tickers:
        directory = f"Caches/{ticker}/D/MA_Momentum/csv_files/"
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if str(f).startswith(directory+"Results_LP"):
                df_ticker = pd.read_csv(str(f))
                df_ticker.rename(columns={"Close": f"{ticker}_Close", "signal": f"{ticker}_Signal"}, inplace=True)
                df_ticker = df_ticker.set_index("Datetime")[[f"{ticker}_Close", f"{ticker}_Signal"]]
                df = pd.concat([df, df_ticker], axis=1)
    df = df.reset_index()
    df["Equity_Signal"] = 1

    print("Creating Multiasset Portfolio backtest")
    initial_portfolio_value = 10000
    pa = PortfolioAllocator(df)   #Consider correlateon filter here too
    pa.create_dates("all")
    pa.select_tickers(tickers)
    portfolio_value, units_ticker = pa.allocate(initial_portfolio_value=initial_portfolio_value, interest_rate=7)
    
    portfolio_value["Benchmark"] = portfolio_value[[f"{ticker}_Close" for ticker in tickers]].mean(axis=1)
    portfolio_value["Benchmark"] = portfolio_value["Benchmark"]*initial_portfolio_value/portfolio_value["Benchmark"].iloc[0]
    portfolio_value[["Pvalue", "Benchmark"]].plot()
    plt.show()
    portfolio_value.to_csv("MultiAsset_Results.csv")