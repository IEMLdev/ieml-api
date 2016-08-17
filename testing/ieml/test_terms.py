import unittest

from ieml.ieml_objects.terms import Term
from ieml.script.operator import sc


class TermsTest(unittest.TestCase):
    def test_terms_creation(self):
        t = Term(sc('E:E:A:.'))
        self.assertIsNotNone(t)
        self.assertEqual(str(t), '[E:E:A:.]')
        self.assertEqual(t, Term('[E:E:A:.]'))
        self.assertNotEqual(t, Term('[E:E:B:.]'))