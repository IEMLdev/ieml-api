from pymongo import MongoClient
import bcrypt
from config import DB_ADDRESS, DB_USERS, COLLECTION_USERS

_login_collection = None

def _get_users_collection():
    # TODO : put this in singleton
    global _login_collection
    if _login_collection is None:
        client = MongoClient(DB_ADDRESS)
        _login_collection = client[DB_USERS][COLLECTION_USERS]
    return _login_collection


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
