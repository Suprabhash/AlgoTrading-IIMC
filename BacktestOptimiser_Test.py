import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (15,5)
plt.rcParams['axes.grid'] = False
import seaborn as sns
sns.set_style("whitegrid", {'axes.grid' : False})
from Strategies.RSI.RSI import RSI
from Metrics.Metrics import SharpeRatio
import sys
import os
sys.path.append(os.getcwd())

from BacktestOptimiser.BacktestOptimiser import BacktestOptimiser
from Utils.utils import correlation_filter
from StockScreener.screener import screener
from StockScreener.Nifty50 import tickers as universe_of_stocks
from StockScreener.screener import simple_momentum_rules as rules

if __name__=='__main__':

    print("Selecting Tickers")
    sc = screener(universe_of_stocks=universe_of_stocks, screener_rules=rules)
    ticker = sc.select_tickers(number=1)
    print(f"Tickers selected: {ticker}")

    optimiser = BacktestOptimiser(strategy = RSI, ticker = ticker, data_frequency = 'D')

    print("Getting data")
    optimiser.get_data()

    print("Creating Dates")
    optimiser.create_dates("1_Months")

    print("Adding features")
    optimiser.add_features()

    print("run_backtests"),
    optimiser.run_backtests(use_optimiser="BruteForce",parallelize=True)

    print("Selecting Strategies")
    optimiser.select_strategies(use_optimiser = "BruteForce",parallelize=True)

    print("Checking Selected Strategies")
    optimiser.check_selected_strategies(forward_months=2)

    print("Filtering Strategies")
    optimiser.filter_strategies(filter_function = correlation_filter)

    print("Optimizing weights")
    optimiser.optimize_weights()

    print("Selecting best and mailing results")
    optimiser.select_best_and_mail_results()