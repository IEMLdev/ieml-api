
"""These unit tests are a bit special, they're used against the old database,
 test the output of the new parser/relational DB with the old DB/Parser"""
from models.base_queries import DictionaryQueries
from ieml.parsing import ScriptParser
from testing.helper import *


class BackTestOrdering(unittest.TestCase):

    def setUp(self):
        self.old_dict = DictionaryQueries()
        self.term_parser = ScriptParser()

    def test_ordering(self):
        """checks that the comparison implemented in the term AST also works in the """
        terms = []
        # creating a list of terms
        for entry in self.old_dict.get_all_terms():
            old_term_object = Term(entry["IEML"])
            old_term_object.check()
            term_ast = self.term_parser.parse(entry["IEML"])
            terms.append((old_term_object, term_ast))

        for i in range(len(terms)):
            old_term_i, ast_i = terms[i]
            for j in range(i):
                old_term_j, ast_j = terms[j]
                self.assertEqual(old_term_i > old_term_j,
                                 ast_i > ast_j,
                                 msg="Comparisons not matching between %s and %s" % (str(ast_i), str(ast_j)))


