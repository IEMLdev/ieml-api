import json

from flask_restful import Resource, reqparse
from models import DictionnaryQueries
from ieml.exceptions import ASTException

class BaseHandler(Resource):
    """This is the base abstract handler, instantiates a request parser,
    and simplifies a couple of operations"""

    def __init__(self):
            """The constructor for this abstract class just creates a request_parser"""
            super().__init__()
            self.reqparse = reqparse.RequestParser()

    def do_request_parsing(self):
        self.args = self.reqparse.parse_args()

    def get(self):
        return {"status": "Correc'"}


class BaseDataHandler(BaseHandler):
    def __init__(self):
        """The constructor for this abstract class just creates a request_parser"""
        super().__init__()
        self.reqparse.add_argument("data", required=True, type=str)

    def do_request_parsing(self):
        super().do_request_parsing()
        self.json_data = json.loads(self.args["data"])

class SearchTermsHandler(BaseHandler):
    """Handles the terms search"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionnaryQueries().search_for_terms(self.args["searchstring"])


class ErrorCatcher:

    def __init__(self, post_function):
        self.post = post_function

    def __call__(self, *args, **kwargs):

        try:
            self.post(*args, **kwargs)
        except ASTException as e:
            # probably going to use a table that'll do error type -> json message conversion
            pass