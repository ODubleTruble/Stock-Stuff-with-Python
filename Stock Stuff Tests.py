import stoks

ticker = 'TSLA'
start_date = '2010-01-01'
end_date = '2022-12-21'
stock_data = stoks.get_stock_data(ticker, start_date, end_date)
ema = stoks.ema(stock_data)


print(f'Effectiveness of strats for {ticker} from {start_date} to {end_date}:')

print('Bullish strats:')
print(f'bull eng: {round(stoks.Strats.bullish_engulfing(stock_data, ema)*100, 2)}%')
print(f'piercing: {round(stoks.Strats.piercing(stock_data, ema)*100, 2)}%')
print(f'hammer: {round(stoks.Strats.hammer(stock_data, ema)*100, 2)}%')

print('Bearish strats:')
print(f'bear eng: {round(stoks.Strats.bearish_engulfing(stock_data, ema)*100, 2)}%')
print(f'dark cloud cover: {round(stoks.Strats.dark_cloud_cover(stock_data, ema)*100, 2)}%')
print(f'shooting star: {round(stoks.Strats.shooting_star(stock_data, ema)*100, 2)}%')
