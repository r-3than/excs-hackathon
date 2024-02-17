import json
from threading import Lock
from random import randint
from flask import Flask, render_template, session, request, \
    copy_current_request_context, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from lobby import Lobby

# Socketio stuff, dont touch
async_mode = None


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()



lobbies = []







#######################################
#               ROUTES                #
#######################################
@app.route('/')
def index():
    # Homepage
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/game', methods=["GET", "POST"])
def game():
    # This joins a game

    # Just created a game
    if request.method == "GET":
        code = session.get("code", None)
        if code is None:
            return redirect("/")
    # Joining an existing game
    else:
        code = request.form["room_code"]
        session["code"] = code
        session["display_name"] = request.form["display_name"]
        # NOTE cant do JoinRoom here because this isnt a socket event so we dont have sid

    return render_template("game.html", async_mode=socketio.async_mode)


@app.route('/create', methods=["POST"])
def create():
    # Creates a new lobby then sends the user to join it
    code = randint(1000, 9999)
    while any(lobby for lobby in lobbies if lobby.code == code):
        code = randint(1000, 9999)

    lobby = Lobby(code)
    lobbies.append(lobby)

    session["code"] = code
    session["display_name"] = request.form["display_name"]

    return redirect(url_for("game"))


@app.route("/load_lobby", methods=["POST"])
def load_lobby():
    # Used to handle the form and decide which action to take
    if request.form['action'] == "Create Room":
        return redirect(url_for("create"), 307) # Code 307 passes the POST data along with the reroute
    elif request.form['action'] == "Join Room":
        return redirect(url_for("game"), 307)
    else:
        return redirect("/")











#######################################
#           SOCKET EVENTS             #
#######################################
@socketio.event
def connect():
    # I thought this got called when each client connected but that might no actually be the case
    code = session.get("code", None)

    if code is None:
        return redirect("/")

    lobby = next((l for l in lobbies if l.code == code), None)

    if lobby is None:
        return redirect('/')

    assert isinstance(lobby, Lobby)

    if not request.sid in lobby.players:
        lobby.add_player(request.sid)

    message = {"room": str(code)}
    join(message)

    emit('my_response', {'data': 'Connected', 'count': 0})



@socketio.event
def join(message):
    # This is what actually puts a client into a room
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    print(rooms())
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})



@socketio.event
def my_room_event(message):
    # This is part of the example app, used to send a message to the room
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])

@socketio.event
def my_event(message):
    # Part of the example, just an echo event
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})




if __name__ == '__main__':
    socketio.run(app, host="localhost", port="3000", allow_unsafe_werkzeug=True)
