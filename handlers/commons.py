from handlers.exceptions import MissingField
from .base import BaseDataHandler, BaseHandler
from models import PropositionsQueries, TextQueries, HyperTextQueries, DictionaryQueries

class SearchTermsHandler(BaseHandler):
    """Handles the terms search"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionaryQueries().search_for_terms(self.args["searchstring"])


class TagsUpdateHandler(BaseDataHandler):

    def do_request_parsing(self):
        super().do_request_parsing()
        for field in ["ieml", "type", "tags"]:
            if field not in self.json_data:
                raise MissingField(field)

    def post(self):
        self.do_request_parsing()

        proposition_type_to_db = {"HYPERTEXT": HyperTextQueries,
                                  "TEXT" : TextQueries,
                                  "PROPOSITION" : PropositionsQueries}

        db_connector = proposition_type_to_db[self.args["type"]]()
        db_connector.update_tags(self.args["IEML"], self.args["TAGS"])

        return {}


