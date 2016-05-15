from .base import BaseDataHandler, BaseHandler
from models import PropositionsQueries, TextQueries, HyperTextQueries, DictionaryQueries

class SearchTermsHandler(BaseHandler):
    """Handles the terms search"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionaryQueries().search_for_terms(self.args["searchstring"])


class TagsUpdateHandler(BaseDataHandler):

    def post(self):
        self.reqparse.add_argument("ieml_string", required=True, type=str)
        self.reqparse.add_argument("type", required=True, type=str)
        self.do_request_parsing()


