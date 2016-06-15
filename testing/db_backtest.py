
"""These unit tests are a bit special, they're used against the old database,
 test the output of the new parser/relational DB with the old DB/Parser"""
from models.base_queries import DictionaryQueries
from ieml.parsing import ScriptParser
from testing.helper import *


class BackTestOrdering(unittest.TestCase):

    def setUp(self):
        self.old_dict = DictionaryQueries()
        self.term_parser = ScriptParser()

        self.terms_list = list()
        for entry in self.old_dict.get_all_terms():
            old_term_object = Term(entry["IEML"])
            old_term_object.check()
            term_ast = self.term_parser.parse(entry["IEML"])
            self.terms_list.append((old_term_object, term_ast))

    def test_ordering(self):
        """checks that the comparison implemented in the term AST also works in the """

        for i in range(len(self.terms_list)):
            old_term_i, ast_i = self.terms_list[i]
            for j in range(i):
                old_term_j, ast_j = self.terms_list[j]
                self.assertEqual(old_term_i > old_term_j,
                                 ast_i > ast_j,
                                 msg="Comparisons not matching between %s and %s" % (str(ast_i), str(ast_j)))

    def test_layer(self):
        """Tests if the new parser/ast computes the same layer as the old one"""

        for old_term, term_ast in self.terms_list:
            self.assertEqual(int(old_term.metadata["LAYER"]),
                             term_ast.layer,
                             msg="Layers not matching for %s" % str(term_ast))

    def test_cardinal(self):
        """Tests if the new parser/ast computes the same cardinal as the old one"""

        for old_term, term_ast in self.terms_list:
            self.assertEqual(int(old_term.metadata["TAILLE"]),
                             term_ast.cardinal,
                             msg="Cardinals not  matching for %s" % str(term_ast))
