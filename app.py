import connexion
import handlers
from flask_cors import CORS

app = connexion.App(__name__, specification_dir='api-doc/')
app.add_api('rest_api.yaml')
cors = CORS(app.app, resources={r"/api/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True) # served on the local network