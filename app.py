import connexion
import handlers

app = connexion.App(__name__, specification_dir='api-doc/')
app.add_api('rest_api.yaml')

if __name__ == '__main__':
    app.run(debug=True) # served on the local network