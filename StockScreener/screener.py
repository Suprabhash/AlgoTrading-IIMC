#Screeners

#Sample screener based on momentum
def simple_momentum_rules(tickers):
    import yfinance as yf
    import pandas as pd
    from datetime import datetime
    from datetime import timedelta
    today = datetime.now()
    start = today-timedelta(days=380)
    today = today.strftime('%Y-%m-%d')
    start = start.strftime('%Y-%m-%d')
    res = []
    for ticker in tickers:
        df_ticker = yf.download(ticker, start=start, end=today).rename(columns={"Close": ticker})[[ticker]]
        for roc in [5,21,42,63,126,252]:
            df_ticker[f"{ticker}ROC{roc}"] = df_ticker[[ticker]].pct_change(roc)
        df_ticker.dropna(inplace=True)
        df_ticker["Momentum"] = df_ticker[[column for column in df_ticker.columns if "ROC" in column]].mean(axis=1)
        momentum = df_ticker["Momentum"].iloc[-1]
        res.append({'ticker': ticker, 'momentum': momentum})
    res = pd.DataFrame(res).sort_values(by="momentum", ascending=False).set_index("ticker")
    res = list(res.index)
    return res

class screener:
    def __init__(self, universe_of_stocks, screener_rules):
        self.tickers = universe_of_stocks
        self.screener_rules = screener_rules

    def select_tickers(self, number):
        selected_tickers = self.screener_rules(self.tickers)
        if len(selected_tickers)<number:
            number = len(selected_tickers)
        return selected_tickers[:number]
        