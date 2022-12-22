import yfinance as yf

ticker = 'TSLA'

start_date = '2020-01-01'
end_date = '2021-12-31'

# Downloads historical data on the ticker from the start to end date.
data = yf.download(ticker, start_date, end_date)

# * You can use .to_csv on the data to save it as a csv file. 
#data.to_csv('raw data on the ticker.csv')

# Makes it so you can refer to the data on individuals dates by
# their index number instead of a string representing the date.
data['Date'] = data.index
data = data[["Date", "Open", "High","Low", "Close", "Adj Close", "Volume"]]
data.reset_index(drop=True, inplace=True)

print(data.head())
