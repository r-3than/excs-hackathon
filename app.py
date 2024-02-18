from flask import Flask, jsonify, request, render_template
import Account
import Round
import pandas as pd
import base64
from data_util import select_round_data, split_dataframe, plot_stock_prices#, plot_stock_prices3


app = Flask(__name__)

# Dummy data for user's FF amount
ff_amount = 10000
share_value = 500
user_account = Account.Account('Joe', ff_amount)
tickers = ['AMZN', 'MSFT', 'BA', 'PFE', 'NKE']
selected_data = None
chunks = []
max_val = None
min_val = None

@app.route('/')
def index():
    global selected_data
    global chunks
    global max_val
    global min_val
    # Check if data has already been selected
    if selected_data is None:
        # Data has not been selected yet, so select it
        stock_data = pd.read_csv('data/historical_closing_prices.csv')
        selected_data, max_val, min_val = select_round_data(stock_data, 'ReefRaveDelicacies')
        new_round = Round.Round(selected_data, max_val, min_val)
        chunks = split_dataframe(selected_data)
    else:
        # Data has already been selected, no need to run select_round_data again
        pass 
    plot_buffer = plot_stock_prices(selected_data, 'ReefRaveDelicacies', max_val, min_val)
    plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')
    #return render_template('index.html', plot_base64 = plot_base64)
    #return render_template('logo.html')
    return render_template('main.html')

@app.route('/ff_amount')
def get_ff_amount():
    return jsonify({'ff_amount': user_account.ff_amount}), 200

@app.route('/buy', methods=['POST'])
def buy_stock():
    global ff_amount
    data = request.get_json()
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount to buy.'}), 400
    # Perform buy operation here
    if user_account.action_buy(amount, share_value) != "Insufficient funds":
        ff_amount -= amount
        return jsonify({'message': f'You bought stocks for {amount} FF.', 'ff_amount': ff_amount}), 200
    else:
        return jsonify({'message': "Insufficient funds"})

@app.route('/sell', methods=['POST'])
def sell_stock():
    global ff_amount
    data = request.get_json()
    amount = data.get('amount', 0)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount to sell.'}), 400
    # Perform sell operation here
    if user_account.action_sell(amount, share_value) != "Insufficient funds":
        ff_amount += amount
        return jsonify({'message': f'You sold stocks for {amount} FF.', 'ff_amount': ff_amount}), 200
    else:
        return jsonify({'message': "Insufficient funds"})

if __name__ == '__main__':
    app.run(host='localhost', port=3000)#, debug=True)
