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

def select_round_data(stock_data, ticker, window_size=5, steps=5, chunk_size=30):
    # Get the index of the first day of the data
    start_index = np.random.randint(0, len(stock_data) - (chunk_size+1)*steps)
    # Get the data for the selected stock for 30 consecutive days
    selected_data = stock_data.iloc[start_index:start_index + chunk_size*steps].copy()  # Make a copy to avoid modifying original data
    # Calculate the rolling mean with specified window size
    smoothed_data = selected_data[ticker].rolling(window=window_size, min_periods=1).mean()
    # Handle NaN values, forward fill with the first valid observation
    smoothed_data = smoothed_data.fillna(method='ffill')
    # Concatenate the 'Date' column with the smoothed data
    result_df = pd.concat([selected_data['Date'], smoothed_data], axis=1)
    result_df.columns = ['Date', ticker]  # Rename columns if needed
    max_val = result_df[ticker].max()
    min_val = result_df[ticker].min()
    return result_df, max_val, min_val

def split_dataframe(df, chunk_size=30):
    # Calculate the number of chunks
    num_chunks = len(df) // chunk_size
    # Initialize a list to store the chunks
    chunks = []
    # Initialize the start index for the first chunk
    start_index = 0
    # Iterate over the dataframe and split it into chunks
    for i in range(num_chunks):
        # Calculate the end index for the current chunk
        end_index = start_index + chunk_size
        # Extract the chunk from the dataframe
        chunk = df.iloc[start_index:end_index+1]
        # Append the chunk to the list of chunks
        chunks.append(chunk)
        # Update the start index for the next chunk
        start_index = end_index
    # Check if there are any remaining rows and add them to the last chunk
    remaining_rows = len(df) % chunk_size
    if remaining_rows > 0:
        last_chunk = df.iloc[-remaining_rows:]
        chunks.append(last_chunk)
    return chunks

'''

def plot_stock_prices(stock_data, ticker, max_val, min_val):
    # Convert the 'Date' column to datetime if it's not already in datetime format
    if not pd.api.types.is_datetime64_any_dtype(stock_data['Date']):
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    
    # Plot the smoothed data on a graph using DataFrame index as x-axis values
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data[ticker], color='orange', linewidth=2)  # Assuming the smoothed data is in a column named 'Smoothed_Data'
    # Set plot title and labels
    ax.set_title(f'Stock Prices for {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    # Set x-axis date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.rcParams.update({'font.family': 'Arial', 'font.weight': 'normal', 'font.style': 'normal'})
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

def plot_stock_prices2(stock_data, ticker):
    # Convert the 'Date' column to datetime if it's not already in datetime format
    if not pd.api.types.is_datetime64_any_dtype(stock_data['Date']):
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    
    # Plot the smoothed data on a graph using DataFrame index as x-axis values
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data[ticker], color='orange', linewidth=2)  # Assuming the smoothed data is in a column named 'Smoothed_Data'
    
    # Set the limits of the x-axis and y-axis to crop the graph
    ax.set_xlim(stock_data['Date'].iloc[0], stock_data['Date'].iloc[-1])
    ax.set_ylim(stock_data[ticker].min(), stock_data[ticker].max())
    
    # Remove ticks and labels from both axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Remove grid lines
    ax.grid(False)
    
    # Hide the spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', transparent=True)
    img_buffer.seek(0)
    
    # Clear the plot
    plt.close(fig)
    
    return img_buffer

''' 

def plot_stock_prices(stock_data, ticker, min_val, max_val):
    # Convert the 'Date' column to datetime if it's not already in datetime format
    if not pd.api.types.is_datetime64_any_dtype(stock_data['Date']):
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
    
    # Plot the smoothed data on a graph using DataFrame index as x-axis values
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data[ticker], color='orange', linewidth=2)  # Assuming the smoothed data is in a column named 'Smoothed_Data'
    
    # Set the limits of the x-axis and y-axis to crop the graph
    ax.set_xlim(stock_data['Date'].iloc[0], stock_data['Date'].iloc[-1])
    if min_val is not None and max_val is not None:
        ax.set_ylim(min_val, max_val)
    
    # Remove ticks and labels from both axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Remove grid lines
    ax.grid(False)
    
    # Hide the spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', transparent=True)
    img_buffer.seek(0)
    
    # Clear the plot
    plt.close(fig)
    
    return img_buffer

'''
stock_data = pd.read_csv('data/historical_closing_prices.csv')
selected_data, maxv, minv = select_round_data(stock_data,'ReefRaveDelicacies')
chunks = split_dataframe(selected_data)
for i in chunks:
    plot_buffer = plot_stock_prices3(selected_data, 'ReefRaveDelicacies', maxv, minv)
    plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')
    with open("b64string.txt", "w") as text_file:
        text_file.write(plot_base64)
        text_file.write("\n\n\n\n\n")

    break

'''
#plot_buffer = plot_stock_prices3(selected_data, 'ReefRaveDelicacies', maxv, minv)
#plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')


