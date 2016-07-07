#!/usr/bin/env python
import connexion
import handlers
import json
from flask_cors import CORS
from pymongo import MongoClient
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = connexion.App(__name__, specification_dir='api-doc/')
app.add_api('rest_api.yaml')
app.after_request = lambda *args: None # a dirty hack so flask_cors doesn't screw up
cors = CORS(app.app, resources={r"/*": {"origins": "*"}})
app.app.secret_key = 'ZLX9PUQULLAKKLWDI1B9CDZ34H1LIGCW7CA3OVJYWLWF23UW80ONS0REZQAKJKKSFVPIF037VGIXIVE6AYN5AJJRONF2TFKMLLZM'
app.app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app.app, async_mode=async_mode)

@socketio.on('shake_hands', namespace="/")
def bindScreenNameToThisSocketIOSession(message):
    screen_name = message['screen_name']
    client = MongoClient()
    dbusers = client.dbusers
    dbusers.users.update({"apis.twitter.screen_name": screen_name},
                         {"$set":{"socket_io_session" : request.sid}})


@socketio.on('connect', namespace="/")
def test_connect():
    print("connected, replying hello")
    emit('hello', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace="/")
def test_disconnect():
    client = MongoClient()
    dbusers = client.dbusers
    dbusers.users.update({"apis.twitter.screen_name": session["screen_name"]},
                         {"$set":{"socket_io_session" : None}})
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app.app, host='0.0.0.0', debug=True)