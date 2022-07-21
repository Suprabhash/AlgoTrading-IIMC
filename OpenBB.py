from Data.OpenBBTerminal.openbb_terminal import api as openbb

aapl_data = openbb.stocks.load(
    ticker="aapl",
    start="2021-06-10",
)
aapl_data = openbb.stocks.process_candle(aapl_data)

print(aapl_data)