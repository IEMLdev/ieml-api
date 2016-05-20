from .base import BaseHandler, ErrorCatcher
from models import DictionaryQueries, PropositionsQueries, HyperTextQueries
from ieml import PropositionsParser
from ieml.AST import Word, Sentence, SuperSentence, Term, promote_to, HyperText, Text
import json


class SearchTermsHandler(BaseHandler):
    """Handles the terms search"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionaryQueries().search_for_terms(self.args["searchstring"])


class SearchPropositionNoPromotionHandler(BaseHandler):
    @ErrorCatcher
    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()

        result = []
        parser = PropositionsParser()
        for proposition in PropositionsQueries().search_for_propositions(self.args["searchstring"], SuperSentence):
            proposition_ast = parser.parse(proposition["_id"])
            result.append({"IEML": str(proposition_ast),
                           "ORIGINAL": proposition["TYPE"],
                           "TAGS": proposition["TAGS"],
                           "ORIGINAL_IEML": str(proposition_ast), # this field is there for request homogeneity
                           "PROMOTED_TO" : proposition["TYPE"]}) # (this one as well)

        return result


class SearchPropositionsHandler(BaseHandler):
    """Search for primitives in the database, for all levels"""

    @ErrorCatcher
    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        # 1 is to build a word, 2 a sentence, 3 a supersentence, 4 a USL
        self.reqparse.add_argument("level", required=True, type=int)
        self.do_request_parsing()

        level_to_type_table = {
            1: Term,
            2: Word,
            3: Sentence,
            4: SuperSentence
        }
        max_primitive_level = level_to_type_table[self.args["level"]]

        result = []
        for term in DictionaryQueries().search_for_terms(self.args["searchstring"]):
            result.append({
                "IEML": str(promote_to(Term(term["IEML"]), max_primitive_level)),
                "TYPE": "TERM",
                "TAGS": {"FR": term["TAGS"]["FR"],
                         "EN": term["TAGS"]["EN"]},
                "ORIGINAL_IEML": term["IEML"],
                "PROMOTED_TO": max_primitive_level.__name__.upper()})

        if max_primitive_level > Term:
            parser = PropositionsParser()
            for proposition in PropositionsQueries().search_for_propositions(self.args["searchstring"],
                                                                             max_primitive_level):
                try:
                    proposition_ast = parser.parse(proposition["_id"])
                except Exception:
                    continue

                result.append({"IEML": str(promote_to(proposition_ast, max_primitive_level)),
                               "TYPE": proposition["TYPE"],
                               "TAGS": proposition["TAGS"],
                               "ORIGINAL_IEML": str(proposition_ast),
                               "PROMOTED_TO": max_primitive_level.__name__.upper()})

        return result


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

        result = self.db_connector.check_tag_exist(tag, language) or self.db_connector_hypertext.check_tag_exist(tag, language)

        return {'exist': result}


class BroadSearchHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.reqparse.add_argument("filters", required=True, type=str)

        self.db_connector_term = DictionaryQueries()
        self.db_connector = PropositionsQueries()
        self.db_connector_hypertext = HyperTextQueries()

    def do_request_parsing(self):
        self.args = self.reqparse.parse_args()
        self.filters = json.loads(self.args["filters"])

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
            level = [level_to_type_table[self.filters['level']]]
            if (level == Term or level == Word) and self.filters['category']:
                category = categories[self.filters['category']]

            if level == Term and self.filters['term_type']:
                term_type = term_types[self.filters['term_type']]

        search_string = self.args['searchstring']

        result = self.db_connector.search_propositions(search_string, language, level)
        result.extend(self.db_connector_term.search_terms(search_string, language, category, term_type))
        result.extend(self.db_connector_hypertext.search_request(search_string, language, level))

        return result
