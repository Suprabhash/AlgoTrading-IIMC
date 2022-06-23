import numpy as np

def feature_creator(df):
    #Add Features here
    return df

def add_RSI(input):
    temp = input[0].copy()
    col_name = input[1]
    lookback = input[2]
    if f'RSI{lookback}' not in temp.columns:
        temp[f'RSI{lookback}'] = RSI(temp, col_name, lookback)
    return temp

def RSI(temp, col_name, lookback):
    delta = temp[col_name].diff().dropna()
    ups = delta*0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[lookback-1]] = np.mean(ups[:lookback]) # The first element should be a simple mean average
    ups = ups.drop(ups.index[:(lookback-1)])
    downs[downs.index[lookback-1]] = np.mean(downs[:lookback]) # The first element should be a simple mean average
    downs = downs.drop(downs.index[:(lookback-1)])
    rs = ups.ewm(com=lookback-1, min_periods=0, adjust=False, ignore_na=False).mean()/ \
         downs.ewm(com=lookback-1, min_periods=0, adjust=False, ignore_na=False).mean()
    rsi = round(100 - 100/(1+rs), 2)
    temp[f'RSI{lookback}'] = np.nan
    temp.loc[lookback:,f'RSI{lookback}'] = rsi
    temp[f'RSI{lookback}'].fillna(0, inplace=True)
    return temp[f'RSI{lookback}']