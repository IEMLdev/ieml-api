import functools

from jwt.exceptions import DecodeError

from models.logins import is_user
import jwt
from ..caching import cache
import hashlib

SECRET_CACHE = 'jwt_secret'
PAYLOAD_SALT_CACHE = 'auth_salt'


def authenticate(name, password):
    if not is_user(name, password):
        return {'success': False, 'message': 'Authentication failed. User not found.'}

    token = jwt.encode({
        'name': name,
        'hash': hashlib.sha224(bytes(name, 'utf8') + cache.get(PAYLOAD_SALT_CACHE)).hexdigest()
    }, cache.get(SECRET_CACHE))

    return {"success": True, "token": token.decode('utf8')}


def need_login(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'token' in kwargs:
            token = kwargs["token"]
        elif 'body' in kwargs and 'token' in kwargs["body"]:
            token = kwargs["body"]['token']
        else:
            return {'success': False, 'message': 'Authentication required.'}

        token = bytes(token, 'utf8') #encoding the string into bytes
        try:
            payload = jwt.decode(token, cache.get(SECRET_CACHE))
        except DecodeError:
            return {'success': False, 'message': 'Token expired, please login again.'}

        if 'name' not in payload or 'hash' not in payload or \
                        hashlib.sha224(bytes(payload['name'], 'utf8') + cache.get(PAYLOAD_SALT_CACHE)).hexdigest() != payload['hash']:
            return {'success': False, 'message': 'Invalid token. Either username or password are invalid.'}

        return func(*args, **kwargs)
    return wrapper

