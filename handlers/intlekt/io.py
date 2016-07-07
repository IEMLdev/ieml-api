from app import socketio
from pymongo import MongoClient
from flask_socketio import emit

@socketio.on('shake_hands', namespace="/")
def bind_screen_name_to_this_socket_io_session(message):
    screen_name = message['screen_name']
    session_id = message['session_id']
    print("session_id: " + session_id)
    client = MongoClient()
    dbusers = client.dbusers
    dbusers.users.update({"apis.twitter.screen_name": screen_name},
                         {"$set":{"socket_io_session" : session_id}})


@socketio.on('connect', namespace="/")
def test_connect():
    print("connected, replying hello")
    emit('hello', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace="/")
def test_disconnect():
    # TODO: find a way to clean up the socket_io_session field from the users collection
    # client = MongoClient()
    # dbusers = client.dbusers
    # dbusers.users.update({"apis.twitter.screen_name": session["screen_name"]},
    #                      {"$set":{"socket_io_session" : None}})
    print('Client disconnected')


def push_server_event(screen_name, event_data):
    client = MongoClient()
    dbusers = client.dbusers
    user = dbusers.users.find_one({"apis.twitter.screen_name": screen_name})
    socketio.emit("server_event", event_data,
                  room=user['socket_io_session'])
