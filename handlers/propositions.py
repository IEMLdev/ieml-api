import logging

from ieml.AST.propositions import Term
from .base import BaseHandler, BaseDataHandler
from ieml.AST import Word, Clause, Sentence, SuperClause, SuperSentence, Morpheme
from ieml.exceptions import InvalidNodeIEMLLevel
from .exceptions import MissingField
from ieml import PropositionsParser, USLParser
from models import PropositionsQueries, DictionnaryQueries

class SentenceGraph:

    primitive_type = Word
    multiplicative_type = Clause
    additive_type = Sentence


class SuperSentenceGraph:

    primitive_type = Sentence
    multiplicative_type = SuperClause
    additive_type = SuperSentence

class ValidatorHandler(BaseDataHandler):

    def __init__(self):
        super().__init__()
        self.db_connector = PropositionsQueries()

    def do_request_parsing(self):
        super().do_request_parsing()
        for field in ["graph", "nodes"]:
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
        self.db_connector.save_closed_proposition(proposition_ast, self.json_data["tags"])
        return {"valid" : True, "ieml" : str(proposition_ast)}


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
        return {"valid" : True, "ieml" : str(word_ast)}


class PropositionSearchHandler(BaseHandler):
    """Search for primitives in the database, for all levels"""

    def post(self):
        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.reqparse.add_argument("level", required=True, type=str)
        self.do_request_parsing()

class TextDecompositionHandler(BaseDataHandler):

    def entry(self, node):
        ieml = str(node)
        elem = DictionnaryQueries().exact_ieml_term_search(ieml)
        if elem:
            return {
                "ieml": ieml,
                "tags": {
                    "FR": elem.get("FR"),
                    "EN": elem.get("EN")
                }
            }
        else:
            return {
                "ieml": ieml
            }

    def prefix_walker(self, node):
        result = [self.entry(node)]
        for n in node.childs:
            n_ieml = str(n)
            for child in self.prefix_walker(n):
                child["ieml"] = '/'.join(n, child["ieml"])
                result.append(child)

        return result

    def post(self):
        self.do_request_parsing()

        parser = USLParser()
        text = parser.parse(self.json_data['data']);
        result = self.prefix_walker(text)
        print(result)
        return result