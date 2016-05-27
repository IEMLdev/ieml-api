from flask import Flask
from flask_restful import Api

from handlers import *

app = Flask(__name__)
api = Api(app)


### This is the api's routing table

# Search endpoint
api.add_resource(SearchHandler, '/api/search')


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

# Text decomposition for hyperlinks
api.add_resource(TextDecompositionHandler, '/api/decomposition_text')

api.add_resource(CheckTagExistHandler, '/api/check_tag_exist')

api.add_resource(ElementDecompositionHandler, '/api/element_decomposition')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # served on the local network