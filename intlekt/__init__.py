from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mongorest import MongoRest

app = Flask(__name__)

# TODO: to be in a config file
app.config.update(
    MONGODB_HOST='localhost',
    MONGODB_PORT=27017,
    MONGODB_DB='ieml',
)

db = MongoEngine(app)
api = MongoRest(app)

from . import models, routes
