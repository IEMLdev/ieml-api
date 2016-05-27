from .base import BaseHandler, ErrorCatcher
from models import PropositionsQueries, HyperTextQueries, SearchRequest
from ieml.AST import Word, Sentence, SuperSentence, Term, HyperText, Text
import json

class CheckTagExistHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.reqparse.add_argument("tag", required=True, type=str)
        self.reqparse.add_argument("language", required=True, type=str)

        self.db_connector = PropositionsQueries()
        self.db_connector_hypertext = HyperTextQueries()

    @ErrorCatcher
    def post(self):
        self.do_request_parsing()

        tag = self.args['tag']
        language = self.args['language']

        result = self.db_connector.check_tag_exist(tag, language) or \
                 self.db_connector_hypertext.check_tag_exist(tag, language)

        return {'exist': result}


class SearchHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.reqparse.add_argument("query", required=True, type=str)
        self.filters = None

    def do_request_parsing(self):
        self.args = self.reqparse.parse_args()
        self.filters = json.loads(self.args["query"])

    @ErrorCatcher
    def post(self):
        self.do_request_parsing()

        language_to_tag = {
            '0': "EN",
            '1': "FR"
        }

        level_to_type_table = {
            '0': Term,
            '1': Word,
            '2': Sentence,
            '3': SuperSentence,
            '4': Text,
            '5': HyperText
        }

        categories = {
            '0': 0,#noun,
            '1': 1,#verb,
            '2': 2,#auxiliary
        }

        term_types = {
            '0': 0,#table,
            '1': 1,#cell,
            '2': 2,#paradigm
        }

        language = None
        level = None
        category = None
        term_type = None

        if self.filters['language']:
            language = [language_to_tag[self.filters['language']]]

        if self.filters['level']:
            level = [level_to_type_table[lvl] for lvl in self.filters['level']]

        if (Term in level or Word in level) and self.filters['category']:
            category = categories[self.filters['category']]

        if Term in level and self.filters['term_type']:
            term_type = term_types[self.filters['term_type']]

        search_string = self.filters['search_string']

        return SearchRequest.search_string(search_string, language, level, category, term_type)
