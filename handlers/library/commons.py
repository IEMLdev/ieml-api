from handlers.library.exceptions import MissingField
from ieml import USLParser
from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.AST.tree_metadata import HypertextMetadata, PropositionMetadata, TextMetadata
from ieml.exceptions import CannotParse
from ieml.parsing.parser import PropositionsParser
from models import PropositionsQueries, TextQueries, HyperTextQueries, DictionaryQueries
from .base import BaseDataHandler, BaseHandler


class SearchTermsHandler(BaseHandler):
    """Handles the terms search"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.do_request_parsing()
        return DictionaryQueries().search_for_terms(self.args["searchstring"])


class TagsUpdateHandler(BaseDataHandler):
    """Updates the value of the tag attached to an IEMl object"""

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

    def _gen_proposition_json(self, proposition):
        # if the proposition is promoted, we're getting its origin before building its JSON
        rendered_proposition = proposition.get_promotion_origin() if proposition.is_promotion else proposition
        return {"IEML" : str(rendered_proposition),
                "TYPE" : rendered_proposition.level,
                "TAGS" : rendered_proposition.metadata["TAGS"]}

    def _children_list_json(self, children_list):
        return [self._gen_proposition_json(child) for child in children_list]

    def _decompose_word(self, word_ast):
        return {"substance" : self._children_list_json(word_ast.subst),
                "mode": self._children_list_json(word_ast.mode)}

    def _decompose_sentence(self, sentence_ast):
        """Decomposes and builds the ieml object for a sentence/supersentence"""
        return [{"substance" : self._gen_proposition_json(clause.subst),
                 "attribute" : self._gen_proposition_json(clause.attr),
                 "mode": self._gen_proposition_json(clause.mode)}
                for clause in sentence_ast.children]

    def _decompose_text(self, text_ast):
        return {'text': self._children_list_json(text_ast.children)}

    def _decompose_hypertext(self, hypertext_ast):
        output_list = []

        for (starting, ending, path, literal) in hypertext_ast.transitions:
            output_list.append({
                "substance": str(hypertext_ast.texts[starting]),
                "mode": {"literal": literal, "path": path.to_ieml_list()},
                "attribute": str(hypertext_ast.texts[ending]),
            })

        return output_list

    def post(self):
        self.reqparse.add_argument("ieml_string", required=True, type=str)
        self.do_request_parsing()
        # setting the DB connectors for all types of IEML objects
        PropositionMetadata.set_connector(PropositionsQueries())
        TextMetadata.set_connector(TextQueries())
        HypertextMetadata.set_connector(HyperTextQueries())

        try:
            ieml_hypertext = USLParser().parse(self.args["ieml_string"])
            if ieml_hypertext.strate == 0:# it's a text
                return self._decompose_text(ieml_hypertext.children[0]) # decomposing the first element
            else: # it's an hypertext with more than one element
                return self._decompose_hypertext(ieml_hypertext)

        except CannotParse:
            ieml_proposition = PropositionsParser().parse(self.args["ieml_string"])
            if isinstance(ieml_proposition, Word):
                return self._decompose_word(ieml_proposition)
            elif isinstance(ieml_proposition, (Sentence, SuperSentence)):
                return self._decompose_sentence(ieml_proposition)


def search_library(query):
    pass


def check_library_tag_exists(tag, language):
    pass


def decompose_ieml_element(ieml_string):
    pass

