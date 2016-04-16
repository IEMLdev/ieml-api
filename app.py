from flask import Flask
from flask_restful import Api

from handlers import *

app = Flask(__name__)
api = Api(app)


### This is the api's routing table

# search for a term in the DB
api.add_resource(SearchTermsHandler, '/api/search_terms')
# search for a proposition/term in the DB, returns a normalized list of propositions
api.add_resource(SearchPropositionsHandler, '/api/search_proposition')
# validate and save a word object, and return its IEML string
api.add_resource(WordGraphValidatorHandler, '/api/validate_word')
# validate and save a proposition (sentence or supersentence) graph, and return its IEML string
api.add_resource(GraphValidatorHandler, '/api/validate_tree')
#
api.add_resource(TextDecompositionHandler, '/api/decomposition_text')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # served on the local network