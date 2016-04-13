from flask import Flask, render_template
from flask_restful import Api

from handlers import SearchTermsHandler, WordGraphValidatorHandler

app = Flask(__name__)
api = Api(app)


### This is the api's routing table

api.add_resource(SearchTermsHandler, '/api/search_terms')
api.add_resource(WordGraphValidatorHandler, '/api/validate_word')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # served on the local network