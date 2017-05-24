import unittest

from ieml.ieml_objects.tools import term


class TermsTest(unittest.TestCase):
    def test_terms_creation(self):
        t = term('E:E:A:.')
        self.assertIsNotNone(t)
        self.assertEqual(str(t), '[E:E:A:.]')
        self.assertEqual(t, term('[E:E:A:.]'))
        self.assertNotEqual(t, term('[E:E:B:.]'))

    def test_relations_order(self):
        t = term('M:M:.O:O:.-')
        self.assertListEqual(t.relations.contains, sorted(t.relations.contains))