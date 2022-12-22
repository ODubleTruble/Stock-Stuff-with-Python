import stoks

stock_data = stoks.get_stock_data('TSLA', '2020-01-01', '2022-12-21')

print(stock_data.head())
print(stoks.find_all_candle_types(stock_data))
