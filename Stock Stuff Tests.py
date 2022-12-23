import stoks

stock_data = stoks.get_stock_data('TSLA', '2010-01-01', '2022-12-21')
ema = stoks.ema(stock_data)

print(f'bull eng: {stoks.Strats.bullish_engulfing(stock_data, ema)}')
print(f'bear eng: {stoks.Strats.bearish_engulfing(stock_data, ema)}')
print(f'piercing: {stoks.Strats.piercing(stock_data, ema)}')
print(f'dark cc: {stoks.Strats.dark_cloud_cover(stock_data, ema)}')

