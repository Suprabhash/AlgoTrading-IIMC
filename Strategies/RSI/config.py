"""
Strategy parameters for the Demo RSI Strategy
"""
from Metrics.Metrics import *
from Utils.utils import frange

params_searchspace = {
    "lookbacks": frange(14, 16, 2),
    "ub": frange(20,30,10),
    "lb": frange(60,70,10)
}

metrics = [SharpeRatio]
number_selected_strategies = 2000
number_selected_filteredstrategies = 10
strategy_lookbacks = [24]
number_of_optimisation_periods = [1]
recalib_periods = [12]
num_strategies = [5]
metrics_opt = [rolling_sharpe] #, rolling_sortino, rolling_cagr, maxdrawup_by_maxdrawdown, outperformance]
consider_selected_strategies_over = 1 
starting_points = 1