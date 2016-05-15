from flask import Flask
from flask_restful import Api

from handlers import *

app = Flask(__name__)
api = Api(app)


### This is the api's routing table

# Search endpoint
# search for a term in the DB
api.add_resource(SearchTermsHandler, '/api/search_terms')
# search for a proposition/term in the DB, returns a normalized list of propositions
api.add_resource(SearchPropositionsHandler, '/api/search_proposition')
# search for propositions, without propoting the terms
api.add_resource(SearchPropositionNoPromotionHandler, '/api/search_propositions_no_promomotion')
# search for a text in the DB, return a list of text
api.add_resource(SearchTextHandler, '/api/search_text')


# Proposition validation and saving endpoints
# validate and save a word object, and return its IEML string
api.add_resource(WordGraphCheckerHandler, '/api/validate_word')
api.add_resource(WordGraphSavingHandler, '/api/save_word')

# validate and save a proposition (sentence or supersentence) graph, and return its IEML string
api.add_resource(GraphCheckerHandler, '/api/validate_tree')
api.add_resource(GraphSavingHandler, '/api/save_tree')

# USL validation and saving endpoints
api.add_resource(TextValidatorHandler, '/api/validate_text')
api.add_resource(HyperTextValidatorHandler, '/api/validate_hypertext')

api.add_resource(PropositionPromoter, '/api/promote_proposition')
#
api.add_resource(TextDecompositionHandler, '/api/decomposition_text')

api.add_resource(CheckTagExist, '/api/check_tag_exist')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # served on the local network