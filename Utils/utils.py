from datetime import date
import numpy as np
import decimal
import pandas as pd
import pickle
from tqdm import tqdm
import multiprocessing
from scipy import stats

def frange(start, end, jump):
    naive_list = np.arange(start, end, jump).tolist()
    decimals = []
    for el in naive_list:
        decimals.append(decimal.Decimal(str(el)).as_tuple().exponent)
    final_list = [round(el,-1*max(decimals)) for el in naive_list]
    return final_list

def callable_functions_helper(params):
    param_func_dict = {}
    for num in range(len(params)):
        if callable(params[num]):
            param_func_dict[params[num].__name__] = params[num]
            params[num] = params[num].__name__
    return params, param_func_dict

###
# Strategy Filters
###

def correlation_filter(strategies_df, strategy, strategy_name,number_selected_strategies, start, end):
    returns = pd.DataFrame()
    for i in range(len(strategies_df)):
        with open(f'Caches/{strategy.ticker}/{strategy.frequency}/{strategy_name}/SelectedStrategies/Backtests/{tuple(callable_functions_helper(list(strategies_df.iloc[i]["params"]))[0])}.pkl','rb') as file:
            sreturn = pickle.load(file)
        sreturn=sreturn["equity_curve"]
        sreturn = sreturn.loc[(sreturn["Datetime"]>start) & (sreturn["Datetime"]<=end)].reset_index(drop=True)
        sreturn = sreturn.dropna()
        if i == 0:
            returns = sreturn['S_Return'].to_frame().rename(columns={'S_Return': f'Strategy{i+1}'}).set_index(sreturn["Datetime"])
        else:
            returns = pd.merge(returns, (sreturn['S_Return'].to_frame().rename(columns={'S_Return': f'Strategy{i+1}'}).set_index(sreturn["Datetime"])),left_index=True, right_index=True)


    corr_mat = returns.corr()
    strategies = [column for column in returns]
    selected_strategies = ["Strategy1"]
    strategies.remove("Strategy1")
    last_selected_strategy = "Strategy1"

    while len(selected_strategies) < number_selected_strategies:
        corrs = corr_mat.loc[strategies][last_selected_strategy]
        corrs = corrs.loc[corrs > 0.9]
        strategies = [st for st in strategies if st not in corrs.index.to_list()]
        if len(strategies) == 0:
            break
        strat = strategies[0]
        selected_strategies.append(strat)
        strategies.remove(strat)
        last_selected_strategy = strat

    selected_strategies = strategies_df.iloc[[int(strategy[8:])-1 for strategy in selected_strategies]].reset_index(drop=True)
    return selected_strategies

###
#  Utility functions for processing dates
###

def valid_dates(dates_all):           #Dates until parameter date: change name
    dates = []
    i = 0
    while True:
        dates.append(dates_all[i])
        if dates_all[i] > pd.to_datetime(date.today()):
            break
        i = i + 1
    return dates

def interpret_time_unit(str):
    frequency = {
        "TradingDays": "B",
        "Days": "D",
        "Weeks": "W",
        "Months": "M",
        "Hours": "H",
        "Minutes": "min"
    }

    num = int(str.split('_')[0])
    units = frequency[str.split('_')[1]]
    return num, units


###
# Percentile Scaler
###
def rolling_percentile(inp):
    df = inp[0]
    lookback_percentile = inp[1]
    columns = inp[2]
    for column in columns:
        df[f"{column}_percentile_over_{lookback_percentile}"] = np.nan
        for i in range(len(df)):
            try:
                df.loc[df.index[i], f"{column}_percentile_over_{lookback_percentile}"] = stats.percentileofscore(
                    df.iloc[i - lookback_percentile + 1:i][column], df.iloc[i][column])/100
            except:
                continue
        df.loc[:lookback_percentile, f"{column}_percentile_over_{lookback_percentile}"] = np.nan
    return df[[f"{column}_percentile_over_{lookback_percentile}" for column in columns]]

def rolling_percentile_parallelized(df_inp, lookback_percentiles, columns):
    df = df_inp.copy()
    inputs = []
    for lookback_percentile in lookback_percentiles:
        inputs.append([df, lookback_percentile, columns])
    try:
        pool = multiprocessing.Pool(processes=7, maxtasksperchild=1)
        results = pool.map(rolling_percentile, inputs)
    finally: # To make sure processes are closed in the end, even if errors happen
        pool.close()
        pool.join()

    for result in results:
        df = pd.concat([df, result], axis=1)
    return df
