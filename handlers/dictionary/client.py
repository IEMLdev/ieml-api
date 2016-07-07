from flask import session
import uuid
from models.logins import is_user


def authenticate(name, password):
    if not is_user(name, password):
        return {'success': False, 'message': 'Authentication failed. User not found.'}

    token = uuid.uuid4().hex
    session['token'] = token
    return {"success": True, "token": token}


def need_login(func):
    def f():
        token = session.get('token', None)
        if token is None:
            return {'success': False, 'message': 'Authentication required.'}

        return func()
    return f

