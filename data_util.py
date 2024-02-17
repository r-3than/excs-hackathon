import yfinance as yf


def combine_stocks_yh_2(tickers, start_date, end_date):
    '''
    Retrieve the historical returns of multiple stocks/indices for a specific timeframe
    Returns the result as a single pandas DataFrame with a column for each stock/index
    params
        | tickers - list of stock/index symbols to retrieve returns for
        | start_date - start date for fetching historical data
        | end_date - end date for fetching historical data
    return
        | returns - historical returns of specified stocks/indices as a single DataFrame
    '''
    # Download data from yahoo finance API
    data = yf.download(tickers, start = start_date, end = end_date)
    # Extract returns
    data = data.loc[:,('Adj Close', slice(None))]
    data.columns = tickers
    returns = data[tickers].dropna()
    return returns