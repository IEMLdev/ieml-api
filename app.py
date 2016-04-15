from flask import Flask
from flask_restful import Api

from handlers import SearchTermsHandler, WordGraphValidatorHandler, TextDecompositionHandler, GraphValidatorHandler

app = Flask(__name__)
api = Api(app)


### This is the api's routing table

api.add_resource(SearchTermsHandler, '/api/search_terms')
api.add_resource(WordGraphValidatorHandler, '/api/validate_word')
api.add_resource(TextDecompositionHandler, '/api/decomposition_text')
api.add_resource(GraphValidatorHandler, '/api/validate_tree')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # served on the local network