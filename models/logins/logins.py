from pymongo import MongoClient
import bcrypt
from config import DB_ADDRESS

DB_USERS = 'users'
COLLECTION_USERS = 'users'


def _get_users_collection():
    client = MongoClient(DB_ADDRESS)
    return client[DB_USERS][COLLECTION_USERS]


def is_user(name, password):
    user = _get_users_collection().find_one({'_id': name})
    if user is None:
        return False

    return bcrypt.hashpw(bytes(password, 'utf8') + user['salt'], user['salt']) == user['hash']


def save_user(name, password):
    salt = bcrypt.gensalt()

    _get_users_collection().insert({
        '_id': name,
        'salt': salt,
        'hash': bcrypt.hashpw(bytes(password, 'utf8') + salt, salt)
    })
