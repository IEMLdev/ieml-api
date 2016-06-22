import connexion
import handlers
from flask_cors import CORS

app = connexion.App(__name__, specification_dir='api-doc/')
app.add_api('rest_api.yaml')
app.after_request = lambda *args: None # a dirty hack so flask_cors doesn't screw up
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True) # served on the local network