from ieml.AST.propositions import Term
from .base import BaseDataHandler
from ieml.AST import Word, Clause, Sentence, SuperClause, SuperSentence, Morpheme
from ieml.exceptions import InvalidNodeIEMLLevel
from ieml import PropositionsParser
from models import PropositionsQueries

class SentenceGraph:

    primitive_type = Word
    multiplicative_type = Clause
    additive_type = Sentence


class SuperSentenceGraph:

    primitive_type = Sentence
    multiplicative_type = SuperClause
    additive_type = SuperSentence

class QueryValidatorHandler(BaseDataHandler):

    def __init__(self):
        super().__init__()
        self.db_connector = PropositionsQueries()

class GraphValidatorHandler(GraphValidatorHandler):
    """Checks that a give graph representing a sentence/supersentence is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):
        parser = PropositionsParser()
        graph_type = SentenceGraph if self.json_data["validation_type"] == 1 else SuperSentenceGraph
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

        return {"valid" : True, "ieml" : str(proposition_ast)}


class WordGraphValidatorHandler(GraphValidatorHandler):
    """Checks that a give graph representing a word is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):

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
        self.db_handler.save_closed_proposition(word_ast, self.json_data["tag"])
        return {"valid" : True, "ieml" : str(word_ast)}
