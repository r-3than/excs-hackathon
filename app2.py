from flask import Flask, jsonify, request, render_template
import Account
import Round
import Game
import pandas as pd
import base64
from data_util import select_round_data, split_dataframe, plot_stock_prices#, plot_stock_prices3


app = Flask(__name__)

# Dummy data for user's FF amount
# ff_amount = 10000
# share_value = 500
#user_account = Account.Account('Joe', ff_amount)
tickers = ['AMZN', 'MSFT', 'BA', 'PFE', 'NKE']
#selected_data = None
#chunks = []
#max_val = None
#min_val = None

game = Game.Game()
player1 = Account.Account('token1', 'Joe', 10000)
player2 = Account.Account('token2', 'Jane', 10000)
round1 = Round.Round()
game.add_player(player1.player_session_token, player1)
game.add_player(player2.player_session_token, player2)



@app.route('/')
def index():
    global game
    #global selected_data
    #global chunks
    #global max_val
    #global min_val
    # Check if data has already been selected
    if not game.active:
        # Game ended - do something bruv
        pass
    elif game.active_round.round_data is not None:
        # Data has already been selected, no need to run select_round_data again
        pass 
    else:
        game.active_round.generate_round_data('data/historical_closing_prices.csv')
    
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
