import connexion
import handlers
from flask_cors import CORS
from handlers.caching import cache
from handlers.dictionary.client import PAYLOAD_SALT_CACHE, SECRET_CACHE
import os
import binascii
import bcrypt

app = connexion.App(__name__, specification_dir='api-doc/')
app.add_api('rest_api.yaml')
cors = CORS(app.app, resources={r"/api/*": {"origins": "*"}})
app.app.secret_key = 'ZLX9PUQULLAKKLWDI1B9CDZ34H1LIGCW7CA3OVJYWLWF23UW80ONS0REZQAKJKKSFVPIF037VGIXIVE6AYN5AJJRONF2TFKMLLZM'

cache.set(SECRET_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)
cache.set(PAYLOAD_SALT_CACHE, binascii.hexlify(os.urandom(24)), timeout=0)

if __name__ == '__main__':
    app.run(debug=True) # served on the local network