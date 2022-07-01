from . import config
from ..strategy import strategy
import itertools
from Utils.add_features import add_RSI
import numpy as np
import matplotlib.pyplot as plt
from pathos.multiprocessing import ProcessingPool

class RSI(strategy):
    def __init__(self):
        strategy.__init__(self)

    def add_features(self, data, params):
        params = [[data]]+[["Close"]]+params
        inputs = list(itertools.product(*params))
        pool = ProcessingPool(7)
        results = pool.map(add_RSI, inputs)
        pool.clear()
        for result in results:
            data[result.columns[-1]] = result.filter(regex='RSI.*')
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
        lookback = params[0]
        up_threshold = params[1]
        low_threshold = params[2]

        df['RSI'] = df[f'RSI{lookback}']
        df = df.loc[(df.RSI != 0)]
        df['RSI_lag'] = df['RSI'].shift(1)  # This will be the PREVIOUS RSI. This is done so that on any given datetime value, we have both previous and current value in the same row
        df["lb"] = low_threshold
        df["ub"] = up_threshold
        df.dropna()
        df.reset_index(inplace=True, drop=True)

        # Creating buy/sell signals
        # Setting the conditions here
        buy_mask = (df['RSI'] < low_threshold) & (df['RSI_lag'] > low_threshold)
        sell_mask = (df['RSI'] > up_threshold) & (df['RSI_lag'] < up_threshold)
        bval = 1
        sval = 0
        df['signal_bounds'] = np.nan
        df.loc[buy_mask, 'signal_bounds'] = bval
        df.loc[sell_mask, 'signal_bounds'] = sval
        df.signal_bounds = df.signal_bounds.fillna(method="ffill")
        df.signal_bounds = df.signal_bounds.fillna(0)

        df["signal"] = df.signal_bounds
        return df[["Datetime", "signal", "lb", "ub", "RSI"]]


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

        plt.plot(df['Datetime'], df['RSI'], color='black', label='RSI')
        plt.plot(df['Datetime'], df['lb'], color='green', label='Lower Bound')
        plt.plot(df['Datetime'], df['ub'], color='red', label='Upper Bound')

        plt.plot(df.loc[buy_plot_mask]['Datetime'].shift(1), df.loc[buy_plot_mask]['RSI'].shift(1), r'^',
                 ms=15,
                 label="Entry Signal", color='green', markeredgecolor='k', markeredgewidth=1)
        plt.plot(df.loc[sell_plot_mask]['Datetime'].shift(1), df.loc[sell_plot_mask]['RSI'].shift(1), r'^',
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
        feature_space = [config.params_searchspace["lookbacks"]]
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



