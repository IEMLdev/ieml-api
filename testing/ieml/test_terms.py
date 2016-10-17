import unittest

from ieml.ieml_objects.terms import Term
from ieml.script.constants import CONTAINED_RELATION
from ieml.script.operator import sc
from models.relations.relations import RelationsConnector
from models.relations.relations_queries import RelationsQueries


class TermsTest(unittest.TestCase):
    def test_terms_creation(self):
        t = Term(sc('E:E:A:.'))
        self.assertIsNotNone(t)
        self.assertEqual(str(t), '[E:E:A:.]')
        self.assertEqual(t, Term('[E:E:A:.]'))
        self.assertNotEqual(t, Term('[E:E:B:.]'))

    def test_relations(self):
        term = Term('M:M:.O:O:.-')
        self.assertListEqual([t.script for t in term.relations(CONTAINED_RELATION)],
                             RelationsQueries.relations(term.script, CONTAINED_RELATION))