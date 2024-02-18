import json
from threading import Lock
from random import randint
from flask import Flask, render_template, session, request, \
    copy_current_request_context, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from classes import Player, Lobby

# Socketio stuff, dont touch
async_mode = None


app = Flask(__name__)
app.config["SECRET_KEY"] = "xyz"
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


lobbies = []







#######################################
#               ROUTES                #
#######################################
@app.route('/')
def index():
    print("Homepage request made")
    # Homepage
    return render_template('home.html', async_mode=socketio.async_mode)


@app.route("/main", methods=["POST"])
def main():
    return render_template("main.html")

@app.route('/pregame', methods=["GET", "POST"])
def pregame():
    # Joins a pregame lobby
    print("Join lobby request made")

    # Just created a game
    if request.method == "GET":
        code = session.get("code", None)
        is_lobby_leader = True
    # Joining an existing game
    else:
        code = request.form.get("codeInput", None)
        display_name = request.form.get("nameInput", "Player")
        print(f"Join req: joiner has set session variable as code {code}")
        session["code"] = code
        session["display_name"] = display_name
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

    return render_template("pregame.html", players=player_names, lobby_leader=is_lobby_leader, async_mode=socketio.async_mode)


@app.route('/create_lobby', methods=["POST"])
def create_lobby():
    # Creates a new lobby then sends the user to join it
    print("Create lobby request made")
    code = randint(1000, 9999)
    while any(lobby for lobby in lobbies if lobby.code == code):
        code = randint(1000, 9999)

    lobby = Lobby(code)
    lobbies.append(lobby)
    print(f"A lobby with code {code} has been created! Lobbies are now: {lobbies}")

    session["code"] = code
    session["display_name"] = request.form["nameInput"]

    return redirect(url_for("pregame"))


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











#######################################
#           SOCKET EVENTS             #
#######################################
@socketio.event
def connect():
    # Gets called by each client when they first load the pregame page
    print(f"Conn event: triggered by {request.sid}")
    code = session.get("code", None)

    if code is None:
        print("Conn event: No lobby code set as session variable!")
        return redirect("/")

    lobby = next((l for l in lobbies if str(l.code) == str(code)), None)

    if lobby is None:
        print(f"Conn event: {request.sid} has been unable to find a lobby with code {code}! Lobbies are: {[l.code for l in lobbies]}")
        return redirect('/')

    assert isinstance(lobby, Lobby)

    print(f"Conn event: {request.sid} has found lobby {lobby.code}")

    player = Player(request.sid, session.get("display_name", "Player"))

    if lobby.add_player(player):
        print(f"Conn event: {request.sid} has been added to {lobby.code}")
    else:
        print(f"Conn event: {request.sid} is already in {lobby.code}!")

    message = {"room": str(code)}

    print(f"Conn event: {request.sid} is calling join event with message {message}")

    join(message)

    print(f"Conn event: {request.sid} should have called join event")

    emit('my_response', {'data': 'Connected', 'count': 0})



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




if __name__ == '__main__':
    socketio.run(app, host="localhost", port="3000", allow_unsafe_werkzeug=True)
