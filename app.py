from app import create_app, socketio
import binascii
from handlers.caching import cache
from handlers.dictionary.client import PAYLOAD_SALT_CACHE, SECRET_CACHE
import bcrypt
import os

if __name__ == '__main__':
    app = create_app()
    cache.set(SECRET_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)
    cache.set(PAYLOAD_SALT_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)
    socketio.run(app.app, host='0.0.0.0', debug=True)