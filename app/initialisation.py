from flask_socketio import SocketIO
import multiprocessing
from flask_compress import Compress
import os
socketio = SocketIO()

def create_app():
    import connexion
    from flask_cors import CORS

    # to start new proccess using the spawn method (start a fresh new python interpretor)
    multiprocessing.set_start_method('spawn')

    # Set this variable to "threading", "eventlet" or "gevent" to test the
    # different async modes, or leave it set to None for the application to choose
    # the best option based on installed packages.
    async_mode = None

    if not os.path.isdir('parser'):
        os.mkdir('parser')

    ## init the usl db for dev
    # init_dev_db()

    app = connexion.App(__name__, specification_dir='../api-doc/')
    app.add_api('dictionary_editor.yaml')
    app.add_api('intlekt.yaml')

    app.after_request = lambda *args: None # a dirty hack so flask_cors doesn't screw up
    cors = CORS(app.app, resources={r"/*": {"origins": "*"}})
    app.app.secret_key = 'ZLX9PUQULLAKKLWDI1B9CDZ34H1LIGCW7CA3OVJYWLWF23UW80ONS0REZQAKJKKSFVPIF037VGIXIVE6AYN5AJJRONF2TFKMLLZM'
    app.app.config['SESSION_TYPE'] = 'filesystem'

    socketio.init_app(app.app)
    Compress(app.app)
    return app