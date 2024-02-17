from flask import Flask, jsonify, request, render_template
import Account

app = Flask(__name__)

# Dummy data for user's FF amount
ff_amount = 10000
share_value = 500
user_account = Account.Account(ff_amount)

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(host='localhost', port=3000, debug=True)
