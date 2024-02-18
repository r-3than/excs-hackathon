from data_util import select_round_data, split_dataframe
import pandas as pd


class Round:
    def __init__(self, chunks=5):
        self.round_data = None
        self.ticker = None
        self.chunks = chunks
        self.max_value = None
        self.min_value = None
        self.active = False
        self.share_price = None

    def generate_round_data(self, filename, ticker):
        stock_data = pd.read_csv(filename)
        self.round_data, self.max_value, self.min_value = select_round_data(stock_data, ticker)
        self.chunks = split_dataframe(self.round_data)

    def start_round(self):
        self.active = True

    def get_round_data(self):
        return self.round_data
    
    def get_chunks(self):
        return self.chunks
    
    def get_max_value(self):
        return self.max_value
    
    def get_min_value(self):
        return self.min_value
    
    def end_round(self):
        self.active = False