import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from io import BytesIO
import base64

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

def select_round_data(stock_data, ticker, window_size=5):
    # Get the index of the first day of the data
    start_index = np.random.randint(0, len(stock_data) - 31)
    # Get the data for the selected stock for 30 consecutive days
    selected_data = stock_data.iloc[start_index:start_index + 30].copy()  # Make a copy to avoid modifying original data
    print(selected_data.head(30))
    # Calculate the rolling mean with specified window size
    smoothed_data = selected_data[ticker].rolling(window=window_size, min_periods=1).mean()
    # Handle NaN values, forward fill with the first valid observation
    smoothed_data = smoothed_data.fillna(method='ffill')
    # Concatenate the 'Date' column with the smoothed data
    result_df = pd.concat([selected_data['Date'], smoothed_data], axis=1)
    result_df.columns = ['Date', ticker]  # Rename columns if needed
    print(result_df.head(30))  # Print the resulting DataFrame for inspection
    return result_df


def plot_stock_prices(stock_data, ticker):
    # Convert the 'Date' column to datetime if it's not already in datetime format
    if not pd.api.types.is_datetime64_any_dtype(stock_data['Date']):
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    
    # Plot the smoothed data on a graph using DataFrame index as x-axis values
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data[ticker], color='orange', linewidth=2)  # Assuming the smoothed data is in a column named 'Smoothed_Data'
    # Set plot title and labels
    ax.set_title(f'Stock Prices for {ticker}', fontsize=16)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Price', fontsize=14)
    # Set x-axis date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.rcParams.update({'font.family': 'Arial', 'font.size': 12, 'font.weight': 'normal', 'font.style': 'normal'})
    #plt.style.use("dark_background") 
    ax.yaxis.set_label_coords(-0.1, 0.5)
    # Remove x-axis ticks
    ax.set_xticks([])
    # Remove grid lines
    ax.grid(False)
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    # Clear the plot
    plt.clf()
    return img_buffer

'''
stock_data = pd.read_csv('data/historical_closing_prices.csv')
selected_data = select_round_data(stock_data,'ReefRaveDelicacies')
plot_buffer = plot_stock_prices2(selected_data, 'ReefRaveDelicacies')
plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')
'''