from classes import Player
from flask import Flask, jsonify, request, render_template
import Account
import Round
import pandas as pd
import base64
from data_util import select_round_data, split_dataframe, plot_stock_prices#, plot_stock_prices3
from flask import Flask, render_template, session, request, \
    copy_current_request_context, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import uuid

app = Flask(__name__)
socketio = SocketIO(app, async_mode=None)
app.config["SECRET_KEY"] = 'secret'
# Dummy data for user's FF amount
ff_amount = 10000
share_value = 500
user_account = Account.Account("token1",'Joe', ff_amount)
tickers = ['AMZN', 'MSFT', 'BA', 'PFE', 'NKE']
selected_data = None
chunks = []
max_val = None
min_val = None

players = []


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
        new_round = Round.Round()
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
    


@socketio.event
def connect():
    # Gets called by each client when they first load the game page

    print(f"Conn event: triggered by {request.sid}")

    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.event
def getPlayer(message):
    # Gets called by each client when they first load the game page
    found = False
    for ply in players:
        if message["data"] == ply.session_id:
            found = True
    if found == True:
        emit('getKey', {'data': message["data"]}) #update token for another 7 days to the client
        return #dont create new key


    cookieUuid = str(uuid.uuid4())
    player = Player(request.sid,cookieUuid, session.get("display_name", "Player"))
    players.append(player)

    print(f"Conn event: triggered by {cookieUuid}")

    emit('getKey', {'data': cookieUuid})

@socketio.event
def join(message):
    # This is what actually puts a client into a room
    print(f"Join event triggered by {request.sid}")
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    print(rooms())
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})



@socketio.event
def my_room_event(message):
    # This is part of the example app, used to send a message to the room
    print(f"Room message event triggered by {request.sid}")
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])

@socketio.event
def my_event(message):
    # Part of the example, just an echo event
    print(f"Echo event triggered by {request.sid}")
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})



@socketio.event
def action(message):
    # Part of the example, just an echo event
    print(f"Echo event triggered by {request.sid}")
    print(message)
    print(message["data"])



if __name__ == '__main__':
    app.run(host='localhost', port=3000)#, debug=True)
