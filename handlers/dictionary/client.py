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
    def wrapper(body):
        if 'token' not in body:
            return {'success': False, 'message': 'Authentication required.'}

        token = bytes(body['token'], 'utf8')
        del body['token']
        payload = jwt.decode(token, cache.get(SECRET_CACHE))

        if 'name' not in payload or 'hash' not in payload or \
                        hashlib.sha224(bytes(payload['name'], 'utf8') + cache.get(PAYLOAD_SALT_CACHE)).hexdigest() != payload['hash']:
            return {'success': False, 'message': 'Invalid token.'}

        return func(body)
    return wrapper

