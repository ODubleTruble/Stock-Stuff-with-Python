import stoks

stock_data = stoks.get_stock_data('TSLA', '2010-01-01', '2022-12-21')
ema = stoks.ema(stock_data)
print(ema[-5:])


print(stoks.Strats.piercing(stock_data))

