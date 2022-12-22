import yfinance as yf
import pandas as pd


DOJI_LIMIT = 0.12


# The ticker of the stock we want to download data from. 
ticker = 'TSLA'

# The start and end date for data to download. 
start_date = '2020-01-01'
end_date = '2022-12-21'

# Downloads historical data on the ticker from the start to end date.
data = yf.download(ticker, start_date, end_date)

# Makes it so you can refer to the data on individuals dates by
# their index number instead of a string representing the date.
data['Date'] = data.index
data = data[["Date", "Open", "High","Low", "Close", "Adj Close", "Volume"]]
data.reset_index(drop=True, inplace=True)

# Turns the data into a pandas dataframe.
df = pd.DataFrame(data, columns = ['Date', 'Open', 'High', 'Low',
                                   'Close', 'Adj Close', 'Volume'])


# Determines if a candle is bullish (returns 1), bearish (2), or a doji (3).
def candle_type(candle):
    '''
    There are 2 main methods I found to determine if a candle is a doji.
    Both utilize a variable, doji_limit, that's a percent.
    
    Method 1:
    1) find the difference of the open and close (this is the size of the body),
    2) find out what percent it is of max(open, close),
    3) that percent must be lower than the doji_limit.
    Some manual estimates (AXNX 0.4%, TSLA 0.5%, DOW 0.1%) show that this method
    can be inconsistent and hard to find an accurate number for.
    
    Method 2:
    1) find the difference of the open and close (body height),
    2) find the difference of the low and high (total height),
    3) find out what percent the body height is of the total height,
    4) that percent must be lower than the doji_limit.
    
    Method 2 seems to be more consistent across stocks of varying sizes, from $63
    to $33,376. For this method, a doji_limit value between 10% and 14% seems to
    be work the best.
    '''
    
    body_size = abs(candle['Open'] - candle['Close'])
    total_size = candle['High'] - candle['Low']
    
    if (body_size / total_size <= DOJI_LIMIT):
        # It's a doji.
        return 3
    elif (candle['Close'] > candle['Open']):
        # It's bullish.
        return 1
    elif (candle['Close'] < candle['Open']):
        # It's bearish.
        return 2


# Function to find the number of doji, bullish candles, and bearish candles
def find_candle_types():
    # the number of each type of candle
    num_doji = 0
    num_bull = 0
    num_bear = 0
    
    # Runs for every row in df.
    for i in range(len(df.index)):
        # Runs if the close is above the open, meaning the candle is bullish.
        if (candle_type(df.iloc[i]) == 1):
            # Increases num_bull by one. 
            num_bull += 1
        elif (candle_type(df.iloc[i]) == 2):
            # Increases num_bear by one. 
            num_bear += 1
        elif (candle_type(df.iloc[i]) == 3):
            # Increases num_doji by one.
            num_doji += 1
            
    return [num_doji, num_bull, num_bear]


print(find_candle_types())
print(df.info)