import unittest

from ieml.dictionary import term, Dictionary
from ieml.dictionary.version import latest_dictionary_version, get_available_dictionary_version


class TermsTest(unittest.TestCase):
    def test_terms_creation(self):
        t = term('E:E:A:.')
        self.assertIsNotNone(t)
        self.assertEqual(str(t), '[E:E:A:.]')
        self.assertEqual(t, term('[E:E:A:.]'))
        self.assertNotEqual(t, term('[E:E:B:.]'))

    def test_relations_order(self):
        t = term('M:M:.O:O:.-')
        self.assertTupleEqual(t.relations.contains, tuple(sorted(t.relations.contains)))

    def test_dictionary(self):
        for v in get_available_dictionary_version()[:6]:
            d = Dictionary(v)
            for t in d:
                self.assertEqual(t.dictionary, d)