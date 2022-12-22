import yfinance as yf
import pandas as pd


# Gets data from a specific stock and returns it in a dataframe.
def get_stock_data(ticker, start_date, end_date):
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
    
    return df


# Determines if a candle is bullish (returns bull), bearish (bear), or a doji (doji).
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
    
    DOJI_LIMIT = 0.12
    
    body_size = abs(candle['Open'] - candle['Close'])
    total_size = candle['High'] - candle['Low']
    
    if (total_size == 0):
        # The low, high, open, and close are all the same.
        # This is extremely rare but technically not impossible, 
        # so this case exists to ensure no ZeroDivisionError.
        return 'empty'
    elif (body_size / total_size <= DOJI_LIMIT):
        # It's a doji.
        return 'doji'
    elif (candle['Close'] > candle['Open']):
        # It's bullish.
        return 'bull'
    elif (candle['Close'] < candle['Open']):
        # It's bearish.
        return 'bear'


# Function to find the number of doji, bullish candles, and bearish candles
def find_all_candle_types(df):
    # the number of each type of candle
    num_doji = 0
    num_bull = 0
    num_bear = 0
    
    # Runs for every row in df.
    for i in range(len(df.index)):
        if (candle_type(df.iloc[i]) == 'bull'):
            # Increases num_bull by one. 
            num_bull += 1
        elif (candle_type(df.iloc[i]) == 'bear'):
            # Increases num_bear by one. 
            num_bear += 1
        elif (candle_type(df.iloc[i]) == 'doji'):
            # Increases num_doji by one.
            num_doji += 1
            
    return [['Bullish', num_bull], ['Bearish', num_bear], ['Doji', num_doji]]


# Candlestick strategies.
class Strats:
    def bullish_engulfing(df):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 1 candle preceding, ends with 3 candles following.
        for i in range(1, dfLen - 3):
            # Runs if the bottom of the candle before this one is above this one's bottom (it's close). 
            # This checks for preceding downtrend.
            if (min(df.iloc[i-1]['Close'], df.iloc[i-1]['Open']) > df.iloc[i]['Close']):
                # Runs if the candle is bearish.
                if (candle_type(df.iloc[i]) == 'bear'):
                    # Checks to see if the next candle opens below and closes above this one's body
                    if (df.iloc[i+1]['Open'] < df.iloc[i]['Close'] and df.iloc[i+1]['Close'] > df.iloc[i]['Open']):
                        # Records the date that this strategy at.
                        date = df.iloc[i]['Date']
                        dates.append([date])
                        # Runs if the candle 2 after the bullish closes higher than the bullish.
                        if (df.iloc[i+3]['Close'] > df.iloc[i+1]['Close']):
                            # The strategy is a success!
                            num_effec += 1
                            dates_succ.append(date)
                            dates[len(dates)-1].append('succ')
                        else:
                            # The strategy is a failure :(
                            dates_fail.append(date)
                            dates[len(dates)-1].append('fail')
        
        # The success rate of the strategy.
        succ_rate = len(dates_succ) / len(dates)
        
        return succ_rate
    
    
    def bearish_engulfing(df):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 1 candle preceding, ends with 3 candles following.
        for i in range(1, dfLen - 3):
            # Runs if the top of the candle before this one is below this one's top (it's close). 
            # This checks for preceding uptrend.
            if (max(df.iloc[i-1]['Close'], df.iloc[i-1]['Open']) < df.iloc[i]['Close']):
                # Runs if the candle is bullish.
                if (candle_type(df.iloc[i]) == 'bull'):
                    # Checks to see if the next candle opens above and closes below this one's body
                    if (df.iloc[i+1]['Open'] > df.iloc[i]['Close'] and df.iloc[i+1]['Close'] < df.iloc[i]['Open']):
                        # Records the date that this strategy at.
                        date = df.iloc[i]['Date']
                        dates.append([date])
                        # Runs if the candle 2 after the bearish closes lower than the bearish.
                        if (df.iloc[i+3]['Close'] < df.iloc[i+1]['Close']):
                            # The strategy is a success!
                            num_effec += 1
                            dates_succ.append(date)
                            dates[len(dates)-1].append('succ')
                        else:
                            # The strategy is a failure :(
                            dates_fail.append(date)
                            dates[len(dates)-1].append('fail')
        
        # The success rate of the strategy.
        succ_rate = len(dates_succ) / len(dates)
        
        return succ_rate
    
    


