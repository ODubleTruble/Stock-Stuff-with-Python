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


# Determines the specific type of candle a candle is.
def candle_name(candle):
    # The size of the body.
    size_body = abs(candle['Close'] - candle['Open'])
    
    # The total size of the candle.
    size_total = candle['High'] - candle['Low']
    
    # The size of the upper shadow.
    size_upper = candle['High'] - max(candle['Close'], candle['Open'])
    
    # The size of the lower shadow.
    size_lower = min(candle['Close'], candle['Open']) - candle['Low']
    
    
    # Determines the candle name.
    if (size_lower > size_body * 2 and size_upper / size_total < 0.1):
        return 'hammer'
    elif (size_upper > size_body * 2 and size_lower / size_total < 0.1):
        return 'shooting star'

    return 'idk'


# Function to find the number of doji, bullish candles, and bearish candles.
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


# Determines if there is a downtrend before this candle.
def downtrend(ema, candle_index):
    # There's a downtrend if this candle's ema is lower than the previous candle's. 
    downtrend = ema[candle_index] < ema[candle_index-1]
    
    # Returns a boolean value of whether or not there's a downtrend preceding this candle. 
    return downtrend


# Determines if there is an uptrend before this candle.
def uptrend(ema, candle_index):
    # There's an uptrend if this candle's ema is above than the previous candle's. 
    uptrend = ema[candle_index] > ema[candle_index-1]
    
    # Returns a boolean value of whether or not there's an uptrend preceding this candle. 
    return uptrend


# Determines if a strat is successful.
# candle_index is the index of the last candle in the pattern
# strat_type is either 'bull' or 'bear'
def is_succ(ema, candle_index, strat_type):
    # Whether or not the strat is successful. 
    succ = False
    
    # Runs if the strat type is bullish, meaning the EMA is supposed to rise. 
    if (strat_type == 'bull'):
        # Runs if the ema increased.
        if (ema[candle_index+2] > ema[candle_index]):
            # Says the strat was successful. 
            succ = True
    elif (strat_type == 'bear'):
        # Runs if the ema decreased.
        if (ema[candle_index+2] < ema[candle_index]):
            # Says the strat was successful. 
            succ = True
    
    return succ


# Finds the exponential moving average from stock data.
# It's used to identify the trend and momentum of a stock's price.
# It is calculated by taking a certain number of periods (e.g., 12, 26, 50) of the
# stock's price and weighting them exponentially. The most recent periods are given
# a higher weight, while older periods are given a lower weight.
def ema(df):
    # The number of periods to include.
    pds_to_incl = 9
    
    # The smoothing factor.
    smooth = 2 / (pds_to_incl + 1)
    
    # A list storing the ema.
    # The first ema will just be the first candle's closing price.
    ema = [df.iloc[0]['Close']]
    
    # Runs for every candle except the first one.
    for i in range(1, len(df.index)):
        ema.append((df.iloc[i]['Close'] * smooth) + (ema[i-1] * (1-smooth)))

    # Returns a list of the ema for each candle.
    return ema


# Candlestick strategies.
class Strats:
    def bullish_engulfing(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 3 candles following.
        for i in range(0, dfLen - 3):
            # Runs if there's a preceding downtrend.
            if (downtrend(ema, i)):
                # Runs if the candle is bearish.
                if (candle_type(df.iloc[i]) == 'bear'):
                    # Checks to see if the next candle opens below and closes above this one's body
                    if (df.iloc[i+1]['Open'] < df.iloc[i]['Close'] and df.iloc[i+1]['Close'] > df.iloc[i]['Open']):
                        # Records the date that this strategy at.
                        date = df.iloc[i]['Date']
                        dates.append([date])
                        # Runs if the strat is successful.
                        if (is_succ(ema, i+1, 'bull')):
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
    
    
    def bearish_engulfing(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 3 candles following.
        for i in range(0, dfLen - 3):
            # Runs if there's a preceding uptrend.
            if (uptrend(ema, i)):
                # Runs if the candle is bullish.
                if (candle_type(df.iloc[i]) == 'bull'):
                    # Checks to see if the next candle opens above and closes below this one's body
                    if (df.iloc[i+1]['Open'] > df.iloc[i]['Close'] and df.iloc[i+1]['Close'] < df.iloc[i]['Open']):
                        # Records the date that this strategy at.
                        date = df.iloc[i]['Date']
                        dates.append([date])
                        # Runs if the strat is successful.
                        if (is_succ(ema, i+1, 'bear')):
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
    
    
    def piercing(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 3 candles following.
        for i in range(0, dfLen - 3):
            # Runs if there's a preceding downtrend.
            if (downtrend(ema, i)):
                # Runs if the candle is bearish.
                if (candle_type(df.iloc[i]) == 'bear'):
                    # Checks if the next candle opens below this one's bottom (close).
                    if (df.iloc[i+1]['Open'] < df.iloc[i]['Close']):
                        # The middle of this candle's body.
                        mid_candle = df.iloc[i]['Close'] + ((df.iloc[i]['Open'] - df.iloc[i]['Close']) / 2)
                        
                        # Checks if the next candle closes above the middle of this one's body.
                        if (df.iloc[i+1]['Close'] > mid_candle):
                            # Records the date that this strategy at.
                            date = df.iloc[i]['Date']
                            dates.append([date])
                            
                            # Runs if the strat is successful.
                            if (is_succ(ema, i+1, 'bull')):
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
    
    
    def dark_cloud_cover(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 3 candles following.
        for i in range(0, dfLen - 3):
            # Runs if there's a preceding uptrend.
            if (uptrend(ema, i)):
                # Runs if the candle is bullish.
                if (candle_type(df.iloc[i]) == 'bull'):
                    # Checks if the next candle opens above this one's top (close).
                    if (df.iloc[i+1]['Open'] > df.iloc[i]['Close']):
                        # The middle of this candle's body.
                        mid_candle = df.iloc[i]['Open'] + ((df.iloc[i]['Close'] - df.iloc[i]['Open']) / 2)
                        
                        # Checks if the next candle closes below the middle of this one's body.
                        if (df.iloc[i+1]['Close'] < mid_candle):
                            # Records the date that this strategy at.
                            date = df.iloc[i]['Date']
                            dates.append([date])
                            
                            # Runs if the strat is successful.
                            if (is_succ(ema, i+1, 'bear')):
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
    
    
    def hammer(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 2 candles following.
        for i in range(0, dfLen - 2):
            # Runs if there's a preceding downtrend.
            if (downtrend(ema, i)):
                # Runs if the candle is a hammer.
                if (candle_name(df.iloc[i]) == 'hammer'):
                    # Records the date that this strategy at.
                    date = df.iloc[i]['Date']
                    dates.append([date])
                    # Runs if the strat is successful.
                    if (is_succ(ema, i, 'bull')):
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
    
    
    def shooting_star(df, ema):
        # The dates where this strategy occurs, succeeds, and fails.
        dates = []
        dates_succ = []
        dates_fail = []
        
        # The number of times this strategy is effective.
        num_effec = 0
        
        # The number of candles.
        dfLen = len(df.index)
        
        # Runs for every row in df (every candle).
        # Starts with 0 candle preceding, ends with 2 candles following.
        for i in range(0, dfLen - 2):
            # Runs if there's a preceding downtrend.
            if (downtrend(ema, i)):
                # Runs if the candle is a shooting star.
                if (candle_name(df.iloc[i]) == 'shooting star'):
                    # Records the date that this strategy at.
                    date = df.iloc[i]['Date']
                    dates.append([date])
                    # Runs if the strat is successful.
                    if (is_succ(ema, i, 'bear')):
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
    
    

