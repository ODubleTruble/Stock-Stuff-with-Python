import stoks

stock_data = stoks.get_stock_data('TSLA', '2010-01-01', '2022-12-21')

print(stoks.Strats.bullish_engulfing(stock_data))

