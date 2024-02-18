from random import randint
from classes import Lobby, Player
from flask import Flask, jsonify, request, render_template
import Account
import Round
import pandas as pd
import base64
from data_util import select_round_data, split_dataframe, plot_stock_prices#, plot_stock_prices3
from flask import Flask, render_template, request, \
    copy_current_request_context, redirect, url_for, make_response
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
market_data = []
max_val = None
min_val = None

players = []
lobbies = []
















@app.route('/ff_amount')
def get_ff_amount():
    return jsonify({'ff_amount': user_account.ff_amount}), 200

@app.route('/')
def index():
    print("Homepage request made")
    # Homepage
    return render_template('home.html', async_mode=socketio.async_mode)





@app.route("/main", methods=["GET", "POST"])
def main():
    session_key = request.cookies.get("seshKey", None)
    code = request.cookies.get("code", None)
    print(f"{session_key} -> Main req: loading main for lobby {code}!")

    if code is None:
        print("Main req: no code found!")
        return redirect("/")

    lobby = next((l for l in lobbies if str(l.code) == str(code)), None)
    if lobby is None:
        print(f"Main req: no lobby found with code {code}! Lobbies are: {[l.code for l in lobbies]}")
        return redirect("/")

    assert(isinstance(lobby, Lobby))

    

    if not session_key in [p.session_id for p in lobby.players]:
        print(f"Main req: Browser {session_key} is no in lobby {code}! Sks are: {[p.session_id for p in lobby.players]}")
        return redirect("/")

    code = request.cookies.get("code", None)
    for lob in lobbies:
        print(lob.code,code)
        if str(lob.code) == str(code):
            return render_template("main.html",market_data=lob.get_market_data(),ticker='ReefRaveDelicacies',code=code)
    return redirect("/")








@app.route('/pregame', methods=["GET", "POST"])
def pregame():
    # Joins a pregame lobby
    print("Join lobby request made")

    tempCODE = None
    tempDISP = None
    # Just created a game
    if request.method == "GET":
        code = request.cookies.get("code", None)
        is_lobby_leader = True
    # Joining an existing game
    else:
        code = request.form.get("codeInput", None)
        display_name = request.form.get("nameInput", "Player")
        #print(f"Join req: joiner has set request.cookies. variable as code {code}")
        tempCODE=code
        tempDISP= display_name
        is_lobby_leader = False

    if code is None:
        print("Join req: no code found!")
        return redirect("/")

    lobby = next((l for l in lobbies if str(l.code) == str(code)), None)
    if lobby is None:
        print(f"Join req: no lobby found with code {code}! Lobbies are: {[l.code for l in lobbies]}")
        return redirect("/")

    assert isinstance(lobby, Lobby)

    # TODO known issue with duplicates
    player_names = [p.display_name for p in lobby.players]
    print(f"Join req: players in lobby {code} are {player_names}")

    resp=make_response(render_template("pregame.html",code=code, players=player_names, lobby_leader=is_lobby_leader, async_mode=socketio.async_mode))
    if tempCODE != None:
        resp.set_cookie("code",tempCODE)
    if tempDISP != None:
        resp.set_cookie("display_name",tempDISP)
    return resp




@app.route('/create_lobby', methods=["POST"])
def create_lobby():
    # Creates a new lobby then sends the user to join it
    print("Create lobby request made")
    code = randint(1000, 9999)
    while any(lobby for lobby in lobbies if lobby.code == code):
        code = randint(1000, 9999)

    lobby = Lobby(code)
    lobbies.append(lobby)
    #print(f"A lobby with code {code} has been created! Lobbies are now: {lobbies}")

    resp = make_response(redirect(url_for("pregame")))

    resp.set_cookie("code", str(code))
    resp.set_cookie("display_name",request.form["nameInput"])

    return resp




@app.route("/find_lobby", methods=["POST"])
def find_lobby():
    # Used to handle the form and decide which action to take
    print("Load lobby request made")
    code = request.form.get("codeInput", "")
    if code == "":
        return redirect(url_for("create_lobby"), 307) # Code 307 passes the POST data along with the reroute
    elif len(code) == 4 and code.isdecimal():
        return redirect(url_for("pregame"), 307)
    else:
        return redirect("/")



@app.route('/endgame', methods=["GET", "POST"])
def endgame():

    # remove from session

    # get lobby code
    # find the lobby with players

    return render_template("end_screen.html", u_position =5, async_mode=socketio.async_mode)


















###########################################
#             SOCKET EVENTS               #
###########################################

@socketio.event
def connect():
    # Gets called by each client when they first load the game page

    print(f"Conn event: triggered by {request.sid}")

    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.event
def joinLobby(message):
    # Gets called by each client when they first load the pregame page
    #print(f"Conn event: triggered by {request.sid}")
    code = request.cookies.get("code", None)

    if code is None:
        #print("Conn event: No lobby code set as request.cookies. variable!")
        return redirect("/")

    lobby = next((l for l in lobbies if str(l.code) == str(code)), None)

    if lobby is None:
        print(f"Conn event: {request.sid} has been unable to find a lobby with code {code}! Lobbies are: {[l.code for l in lobbies]}")
        return redirect('/')

    assert isinstance(lobby, Lobby)

    #print(f"Conn event: {request.sid} has found lobby {lobby.code}")
    

    player = Player(request.sid, message["data"], request.cookies.get("display_name", "Player"))
    for ply in players:
        if request.cookies.get("seshKey") == ply.session_id:
            player = ply

    if player is None:
        print("BIG ERROR - PLAYER NOT FOUND FOLLOWING CREATION")

    if lobby.add_player(player):
        print(f"Conn event: {player.display_name} has been added to {lobby.code}")
    else:
        print(f"Conn event: {request.sid} is already in {lobby.code}!")

    message = {"room": str(code)}
    player_name = request.cookies.get("display_name", "Player")

    #print(f"Conn event: {request.sid} is calling join event with message {message}")

    #join(message)

    #print(f"Conn event: {request.sid} should have called join event")
    
    player_names = []
    for ply in lobby.players:
        player_names.append(ply.display_name)
    for ply in lobby.players:
        emit('newPlayerJoined', {'data': player_names},to=ply.sid)








@socketio.event
def getPlayer(message):
    # Gets called by each client when they first load the game page
    # Makes sure the objs saved sid is always the one theyve been assigned
    # We need sid in order to send events I think
    key=message["data"]
    print(f"GetPlayer event: I am sesh key {key} currently this sid {request.sid}")
    found = False
    for ply in players:
        if message["data"] == ply.session_id:
            print(f"GetPlayer event: force setting {key}s saved sid {ply.sid} to current {request.sid}")
            found = True
            ply.sid = request.sid
            print(f"GetPlayer event: {key}s saved side {ply.sid} should match current {request.sid}")
    if found == True:
        emit('getKey', {'data': message["data"]}) #update token for another 7 days to the client
        return #dont create new key

    # If player didnt exist, generate them a session key and create them
    print(f"Player for sid {request.sid} did not already exist so generating them a perma session key")
    cookieUuid = str(uuid.uuid4())
    player = Player(request.sid,cookieUuid, request.cookies.get("display_name", "Player"))
    players.append(player)

    emit('getKey', {'data': cookieUuid})






@socketio.event
def beginGame():
    print(f"Bg event: triggered by {request.sid}")
    code = request.cookies.get("code", None)

    if code is None:
        print("Bg event: No lobby code set as request.cookies. variable!")
        return redirect("/")

    lobby = next((l for l in lobbies if str(l.code) == str(code)), None)

    if lobby is None:
        print(f"Bg event: {request.sid} has been unable to find a lobby with code {code}! Lobbies are: {[l.code for l in lobbies]}")
        return redirect('/')

    assert isinstance(lobby, Lobby)

    print(f"Bg event: {request.sid} has found lobby {lobby.code} with players {[p.display_name for p in lobby.players]}")

    for ply in lobby.players:
        emit('beginGame', to=ply.sid)









@socketio.event
def join(message):
    # This is what actually puts a client into a room
    #print(f"Join event triggered by {request.sid}")
    join_room(message['room'])
    #request.cookies.['receive_count'] = request.cookies.get('receive_count', 0) + 1
    #print(rooms())
    




@socketio.event
def my_room_event(message):
    pass
    # This is part of the example app, used to send a message to the room
    #print(f"Room message event triggered by {request.sid}")
    #request.cookies.['receive_count'] = request.cookies..get('receive_count', 0) + 1
    #emit('my_response',
    #     {'data': message['data'], 'count': request.cookies.['receive_count']},
    #     to=message['room'])




@socketio.event
def my_event(message):
    pass
    # Part of the example, just an echo event
    #print(f"Echo event triggered by {request.sid}")
 #   request.cookies.['receive_count'] = request.cookies..get('receive_count', 0) + 1
  #  emit('my_response',
#         {'data': message['data'], 'count': request.cookies.['receive_count']})



@socketio.event
def action(message):
    # Part of the example, just an echo event
    print(f"Echo event triggered by {request.sid}")
    print(message)
    found = False
    for ply in players:
        if ply.session_id == request.cookies.get("seshKey"):
                found = True
                break
    if found == False:
        return
    if not str(message["qty"]).isnumeric():
        return
    for lob in lobbies:
        print("LOB CODES",lob.code)
        print("user CODES",message["lobby_code"])
        if str(message["lobby_code"]) == str(lob.code):

            if message["action"] == "end":
                next_graph=lob.nextRound()
                if(next_graph == -1):
                    for player in lob.players:
                        emit("endgame", to=player.sid)
                #print("^^")
                #print(lob.players)
                for upply in lob.players:
                    print("SENDING TO",upply.display_name)
                    emit("show_round",{"data":next_graph,"stock":upply.share_c,"ff":upply.ff_amount},to=upply.sid)
                    print("I WANT TO SEND TO ",upply.sid)
            else:
                lob.setChoice(ply,message["action"],message["qty"])






if __name__ == '__main__':
    app.run(host='localhost', port=3000)#, debug=True)
