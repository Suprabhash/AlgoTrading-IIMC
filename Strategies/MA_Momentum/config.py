"""
Strategy parameters for the Demo RSI Strategy
"""
from Metrics.Metrics import *
from Utils.utils import frange

params_searchspace = {
    "percentile_lookbacks": [76],
    "percentile_volume_for_trade": [0.9],
    "percentile_barsize_for_buy": [0.91],
    "percentile_barsize_for_sell": [0.1]
}

metrics = [SharpeRatio]
number_selected_strategies = 2000
number_selected_filteredstrategies = 10
strategy_lookbacks = [12]
number_of_optimisation_periods = [1]
recalib_periods = [12]
num_strategies = [5]
metrics_opt = [outperformance] #, rolling_sortino, rolling_cagr, maxdrawup_by_maxdrawdown, outperformance]
consider_selected_strategies_over = 1 
starting_points = 1