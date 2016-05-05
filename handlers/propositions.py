import logging

from ieml import PropositionsParser
from ieml.AST import Word, Sentence, SuperSentence, Morpheme, Term, promote_to
from ieml.AST.tools import SentenceGraph, SuperSentenceGraph
from ieml.exceptions import InvalidNodeIEMLLevel
from models import PropositionsQueries, DictionaryQueries, PropositionAlreadyExists
from .base import BaseHandler, BaseDataHandler
from .exceptions import MissingField,PromotingToInvalidLevel


class ValidatorHandler(BaseDataHandler):
    """Abstract handler for both proposition-related handlers. Factorizes the JSON data field-checking"""

    def __init__(self):
        super().__init__()
        self.db_connector = PropositionsQueries()

    def do_request_parsing(self):
        super().do_request_parsing()
        for field in ["graph", "nodes", "tags"]:
            if field not in self.json_data:
                raise MissingField(field)


class GraphValidatorHandler(ValidatorHandler):
    """Checks that a give graph representing a sentence/supersentence is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):
        self.do_request_parsing()

        parser = PropositionsParser()
        if "validation_type" in self.json_data:
            graph_type = SentenceGraph if self.json_data["validation_type"] == 1 else SuperSentenceGraph
        else:
            logging.warning("Couldn't find validation_type field, defaulting to sentence level")
            graph_type = SentenceGraph

        nodes_table = {}
        for node in self.json_data["nodes"]:
            nodes_table[node["id"]] = parser.parse(node["ieml_string"])
            if not isinstance(nodes_table[node["id"]], graph_type.primitive_type):
                raise InvalidNodeIEMLLevel(node["id"])

        # transforming the vertices into clauses or superclauses
        multiplication_elems = []
        for vertice in self.json_data["graph"]:
            new_element = graph_type.multiplicative_type(nodes_table[vertice["substance"]],
                                                         nodes_table[vertice["attribute"]],
                                                         nodes_table[vertice["mode"]])
            multiplication_elems.append(new_element)

        #OH WAIT, we can make it into a sentence/supersentence now!
        proposition_ast = graph_type.additive_type(multiplication_elems)
        # asking the proposition to check itself
        proposition_ast.check()
        proposition_ast.order()
        self.db_connector.save_closed_proposition(proposition_ast, self.json_data["tags"])
        return {"valid": True, "ieml": str(proposition_ast)}


class WordGraphValidatorHandler(ValidatorHandler):
    """Checks that a give graph representing a word is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):
        self.do_request_parsing()

        parser = PropositionsParser()
        nodes_table = {}
        for node in self.json_data["nodes"]:

            nodes_table[node["id"]] = parser.parse(node["ieml_string"])
            if not isinstance(nodes_table[node["id"]], Term):
                raise InvalidNodeIEMLLevel(node["id"])

        # making the two morphemes and then the word using the two term lists
        substance_morpheme = Morpheme([nodes_table[id] for id in self.json_data["graph"]["substance"]])
        mode_morpheme = Morpheme([nodes_table[id] for id in self.json_data["graph"]["mode"]])
        word_ast = Word(substance_morpheme, mode_morpheme)

        # asking the proposition to check itself
        word_ast.check()
        self.db_connector.save_closed_proposition(word_ast, self.json_data["tags"])
        return {"valid": True, "ieml": str(word_ast)}


class SearchPropositionNoPromotionHandler(BaseHandler):
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
                           "ORIGINAL_IEML": str(proposition_ast)})

        return result


class SearchPropositionsHandler(BaseHandler):
    """Search for primitives in the database, for all levels"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.reqparse.add_argument("level", required=True, type=int) # 1 is word, 2 sentence, 3 supersentence
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
            term["IEML"] = str(promote_to(Term(term["ieml"]), max_primitive_level))
            term["ORIGINAL"] = "TERM"
            term["TAGS"] = {"FR" : term["natural_language"]["FR"],
                            "EN" : term["natural_language"]["EN"]}
            term["ORIGINAL_IEML"] = term["ieml"]

            result.append(term)

        parser = PropositionsParser()
        for proposition in PropositionsQueries().search_for_propositions(self.args["searchstring"],
                                                                         max_primitive_level):
            proposition_ast = parser.parse(proposition["_id"])
            result.append({"IEML" : str(promote_to(proposition_ast, max_primitive_level)),
                           "ORIGINAL" : proposition["TYPE"],
                           "TAGS" : proposition["TAGS"],
                           "ORIGINAL_IEML": str(proposition_ast)})

        return result


class PropositionPromoter(BaseHandler):
    def __init__(self):
        super().__init__()
        self.reqparse.add_argument("ieml", required=True, type=str)
        self.reqparse.add_argument("promotion_lvl", required=True, type=str)
        self.reqparse.add_argument("term", required=True, type=int)

        self.db_connector_proposition = PropositionsQueries()
        self.db_connector_term = DictionaryQueries()
        self.level_to_class = {
            '0': Term,
            '1': Word,
            '2': Sentence,
            '3': SuperSentence
        }
        self.parser = PropositionsParser()

    def post(self):
        self.do_request_parsing()

        if self.args['term']:
            proposition_entry = self.db_connector_term.exact_ieml_term_search(self.args['ieml'])
            proposition_entry['TAGS'] = {
                'FR': proposition_entry['FR'],
                'EN': proposition_entry['EN']
            }
            proposition = self.parser.parse('[' + self.args['ieml'] + ']')
        else:
            proposition = self.parser.parse(self.args['ieml'])
            proposition_entry = self.db_connector_proposition.exact_ieml_search(proposition)

        level = self.args['promotion_lvl']
        if level not in self.level_to_class:
            raise PromotingToInvalidLevel()

        try:
            self.db_connector_proposition.save_promoted_proposition(
                promote_to(proposition, self.level_to_class[level]),
                proposition_entry['TAGS'],
                proposition)
        except PropositionAlreadyExists:
            pass

        return {'valid': True}
