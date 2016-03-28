from .base import BaseDataHandler
from ieml import *
class GraphValidatorHandler(BaseDataHandler):
    """Checks that a give graph representing a sentence/supersentence is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):
        if self.json_data["validation_type"] == 1:
            proposition_graph = SentenceGraph(self.json_data["nodes"])
            graph_checker_type = SentenceGraphChecker
        else:
            proposition_graph = SuperSentenceGraph(self.json_data["nodes"])
            graph_checker_type = SuperSentenceGraphChecker

        for vertice_data in self.json_data["graph"]:
            proposition_graph.add_vertice(vertice_data["substance"], vertice_data["attribute"], vertice_data["mode"])
        proposition_graph.validate(graph_checker_type)
        ast_tree = proposition_graph.to_ast()
        ast_tree.check()
        return {"valid" : True, "ieml" : str(ast_tree)}


class WordGraphValidatorHandler(BaseDataHandler):
    """Checks that a give graph representing a word is well formed, and if it is,
    returns the corresponding IEML string"""

    def post(self):
        word_graph = WordsGraph(self.json_data["nodes"],
                                self.json_data["graph"]["substance"],
                                self.json_data["graph"]["mode"])
        word_graph.validate(WordGraphChecker)
        ast_tree = word_graph.to_ast()
        ast_tree.check()
        return {"valid" : True, "ieml" : str(ast_tree)}