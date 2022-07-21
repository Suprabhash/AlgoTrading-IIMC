from . import config
from ..strategy import strategy
import itertools
from Utils.utils import rolling_percentile
import numpy as np
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool
import warnings
warnings.filterwarnings("ignore")

class MA_Momentum(strategy):
    def __init__(self):
        strategy.__init__(self)

    def add_features(self, data, params):
        data["Size_of_Candle"] = data["Close"]-data["Open"]

        #Adding rolling percentile of Volume levels
        params_inp = [[data]]+params+[[["Volume"]]]
        inputs = list(itertools.product(*params_inp))
        pool = ProcessingPool(7)
        results = pool.map(rolling_percentile, inputs)
        pool.clear()
        for result in results:
            data[result.columns[-1]] = result.filter(regex='Volume_percentile_over_.*')

        #Adding rolling percentiles of size of candles
        params_inp = [[data]]+params+[[["Size_of_Candle"]]]
        inputs = list(itertools.product(*params_inp))
        pool = ProcessingPool(7)
        results = pool.map(rolling_percentile, inputs)
        pool.clear()
        for result in results:
            data[result.columns[-1]] = result.filter(regex='Size_of_Candle_percentile_over_.*')
        self.data = data

        return self.data

    def create_signals(self, df_input, *params):   #Add a risk management module that checks while creating signals
        """
            Creates signals based on RSI values and its defined thresholds. A buy signal is created when RSI crosses over lower bound from bottom to top
            A sell signal is created when RSI crosses over upper bound from top to bottom
            :param df: Receives the OHLCV data frame with a column for Datetime
            :param params: A list of the lookback, lower bound and  upper bound
            :return: Returns a dataframe consisting of the Datetime and the signal
            """
        df = df_input.copy()
        params = params[0]
        percentile_lookback = params[0]
        percentile_volume_for_trade = params[1]
        percentile_barsize_for_buy_max = params[2]
        percentile_barsize_for_buy_min = params[3]
        percentile_barsize_for_sell = params[4]

        df['Volume_percentile'] = df[f'Volume_percentile_over_{percentile_lookback}']
        df['BarSize_percentile'] = df[f'Size_of_Candle_percentile_over_{percentile_lookback}']
        df["percentile_volume_for_trade"] = percentile_volume_for_trade
        df["percentile_barsize_for_buy_max"] = percentile_barsize_for_buy_max
        df["percentile_barsize_for_buy_min"] = percentile_barsize_for_buy_min
        df["percentile_barsize_for_sell"] = percentile_barsize_for_sell
        df.dropna()
        df.reset_index(inplace=True, drop=True)

        # Creating buy/sell signals
        # Setting the conditions here
        buy_mask = (df['Volume_percentile'] > percentile_volume_for_trade) & (percentile_barsize_for_buy_max> df['BarSize_percentile']) & (df['BarSize_percentile']> percentile_barsize_for_buy_min)
        sell_mask = (df['Volume_percentile'] > percentile_volume_for_trade) & (df['BarSize_percentile'] < percentile_barsize_for_sell)
        bval = 1
        sval = 0
        df['signal_bounds'] = np.nan
        df.loc[buy_mask, 'signal_bounds'] = bval
        df.loc[sell_mask, 'signal_bounds'] = sval
        df.signal_bounds = df.signal_bounds.fillna(method="ffill")
        df.signal_bounds = df.signal_bounds.fillna(0)

        df["signal"] = df.signal_bounds
        return df[["Datetime", "signal", "Volume_percentile", "BarSize_percentile", "percentile_volume_for_trade", "percentile_barsize_for_buy_max", "percentile_barsize_for_sell"]]


    def plotting_function(self, df, save_to=None):
        bval = 1
        sval = 0
        buy_plot_mask = ((df.signal.shift(-1) == bval) & (df.signal == sval))
        sell_plot_mask = ((df.signal.shift(-1) == sval) & (df.signal == bval))

        plt.plot(df['Datetime'], df['Close'], color='black', label='Price')
        plt.plot(df.loc[buy_plot_mask]['Datetime'], df.loc[buy_plot_mask]['Close'], r'^', ms=15,
                 label="Entry Signal", color='green', markeredgecolor='k', markeredgewidth=1)
        plt.plot(df.loc[sell_plot_mask]['Datetime'], df.loc[sell_plot_mask]['Close'], r'^', ms=15,
                 label="Exit Signal", color='red', markeredgecolor='k', markeredgewidth=1)
        plt.title('Strategy Backtest')
        plt.legend(loc=0)
        d_color = {}
        d_color[1] = '#90ee90'  ## light green
        d_color[-1] = "#ffcccb"  ## light red
        d_color[0] = '#ffffff'

        j = 0
        for i in range(1, df.shape[0]):
            if np.isnan(df.signal[i - 1]):
                j = i
            elif (df.signal[i - 1] == df.signal[i]) and (i < (df.shape[0] - 1)):
                continue
            else:
                plt.axvspan(df['Datetime'][j], df['Datetime'][i],
                            alpha=0.5, color=d_color[df.signal[i - 1]], label="interval")
                j = i
        if save_to != None:
            plt.savefig(save_to)
        else:
            plt.show()
        plt.clf()

        plt.plot(df['Datetime'], df['Volume_percentile'], color='black', label='Volume_percentile')
        plt.plot(df['Datetime'], df['BarSize_percentile'], color='blue', label='BarSize_percentile')
        plt.plot(df['Datetime'], df['percentile_volume_for_trade'], color='yellow', label='percentile_volume_for_trade')
        plt.plot(df['Datetime'], df['percentile_barsize_for_buy_max'], color='green', label='percentile_barsize_for_buy_max')
        plt.plot(df['Datetime'], df['percentile_barsize_for_sell'], color='red', label='percentile_barsize_for_sell')

        plt.plot(df.loc[buy_plot_mask]['Datetime'].shift(1), df.loc[buy_plot_mask]['BarSize_percentile'].shift(1), r'^',
                 ms=15,
                 label="Entry Signal", color='green', markeredgecolor='k', markeredgewidth=1)
        plt.plot(df.loc[sell_plot_mask]['Datetime'].shift(1), df.loc[sell_plot_mask]['BarSize_percentile'].shift(1), r'^',
                 ms=15,
                 label="Exit Signal", color='red', markeredgecolor='k', markeredgewidth=1)
        plt.title('Strategy Backtest')
        plt.legend(loc=0)
        d_color = {}
        d_color[1] = '#90ee90'  ## light green
        d_color[-1] = "#ffcccb"  ## light red
        d_color[0] = '#ffffff'

        j = 0
        for i in range(1, df.shape[0]):
            if np.isnan(df.signal[i - 1]):
                j = i
            elif (df.signal[i - 1] == df.signal[i]) and (i < (df.shape[0] - 1)):
                continue
            else:
                plt.axvspan(df['Datetime'][j], df['Datetime'][i],
                            alpha=0.5, color=d_color[df.signal[i - 1]], label="interval")
                j = i
        if save_to != None:
            plt.savefig(save_to)
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def get_optimization_params():
        feature_space = [config.params_searchspace["percentile_lookbacks"]]
        parameter_searchspace = [config.params_searchspace[key] for key in config.params_searchspace.keys()]
        metric_searchspace = [config.metrics]
        strategy_lookbacks = config.strategy_lookbacks
        number_of_optimisation_periods = config.number_of_optimisation_periods
        recalib_periods = config.recalib_periods
        num_strategies = config.num_strategies
        metrics_opt = config.metrics_opt
        number_selected_filteredstrategies = config.number_selected_filteredstrategies
        consider_selected_strategies_over = config.consider_selected_strategies_over
        number_selected_strategies = config.number_selected_strategies
        starting_points = config.starting_points
        return { "feature_space": feature_space, "parameter_searchspace": parameter_searchspace, "metric_searchspace": metric_searchspace,
                "strategy_lookbacks": strategy_lookbacks,
                "number_of_optimisation_periods": number_of_optimisation_periods,
                "recalib_periods": recalib_periods, "num_strategies": num_strategies, "metrics_opt": metrics_opt,
                "number_selected_filteredstrategies": number_selected_filteredstrategies,
                "consider_selected_strategies_over": consider_selected_strategies_over,
                "number_selected_strategies": number_selected_strategies,
                "starting_points": starting_points}



