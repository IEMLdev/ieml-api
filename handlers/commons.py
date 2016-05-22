from handlers.exceptions import MissingField
from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.exceptions import CannotParse
from ieml.parsing.parser import PropositionsParser
from .base import BaseDataHandler, BaseHandler
from models import PropositionsQueries, TextQueries, HyperTextQueries, DictionaryQueries
from ieml import USLParser

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


class ElementDecompositionHandler(BaseHandler):
    """Decomposes any IEML string input into its sub elements"""

    def _childs_list_ieml(self, childs_list):
        return [str(child) for child in childs_list]

    def _decompose_word(self, word_ast):
        return {"subst" : self._childs_list_ieml(word_ast.subst),
                "mode": self._childs_list_ieml(word_ast.mode)}

    def _decompose_sentence(self, sentence_ast):
        """Decomposes and builds the ieml object for a sentence/supersentence"""
        return [{"subst" : self._childs_list_ieml(clause.subst),
                 "attribute" : self._childs_list_ieml(clause.attr),
                 "mode": self._childs_list_ieml(clause.mode)}
                for clause in sentence_ast.childs]

    def _decompose_text(self, text_ast):
        return self._childs_list_ieml(text_ast.childs)

    def _decompose_hypertext(self, hypertext_ast):
        return self._childs_list_ieml(hypertext_ast.childs)

    def post(self):
        self.reqparse.add_argument("ieml_string", required=True, type=str)
        self.do_request_parsing()

        try:
            ieml_hypertext = USLParser().parse(self.args["ieml_string"])
            if len(ieml_hypertext.childs) == 1:# it's a text
                return self._decompose_text(ieml_hypertext.childs[0]) # decomposing the first element
            else: # it's an hypertext with more than one element
                return self._decompose_hypertext(ieml_hypertext)

        except CannotParse:
            ieml_proposition = PropositionsParser().parse(self.args["ieml_string"])
            if isinstance(ieml_proposition, Word):
                return self._decompose_word(ieml_proposition)
            elif isinstance(ieml_proposition, (Sentence, SuperSentence)):
                return self._decompose_sentence(ieml_proposition)

