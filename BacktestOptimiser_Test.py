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

if __name__=='__main__':

    optimiser = BacktestOptimiser(strategy = RSI, ticker = "^NSEI", data_frequency = 'D')

    print("Getting data")
    optimiser.get_data()

    print("Creating Dates")
    optimiser.create_dates("3_Months")

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