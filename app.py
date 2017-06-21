from app import create_app, socketio
import binascii

from config import API_PORT
from handlers.caching import cache
from handlers.dictionary.client import PAYLOAD_SALT_CACHE, SECRET_CACHE
import os


if __name__ == '__main__':
    app = create_app()

    if not cache.has(SECRET_CACHE):
        cache.set(SECRET_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)

    if not cache.has(PAYLOAD_SALT_CACHE):
        cache.set(PAYLOAD_SALT_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)

    socketio.run(app.app, host='0.0.0.0', port=API_PORT, debug=True)