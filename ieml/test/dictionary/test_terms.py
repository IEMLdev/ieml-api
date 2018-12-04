import unittest

from ieml.dictionary_old import term, Dictionary
from ieml.dictionary_old.version import latest_dictionary_version, get_available_dictionary_version


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

    def test_root(self):
        d = Dictionary()
        roots = set()
        for r in d.roots:
            self.assertTrue(r.is_root)
            roots.add(r)

        for t in d:
            if t in roots:
                continue
            self.assertFalse(t.is_root)


    def test_phonetic(self):
        self.assertEqual(term("A:").phonetic, "A")
        self.assertEqual(term("wa.").phonetic, "wa.")
        self.assertEqual(term("we.M:M:.-").phonetic, "weMM-")
        self.assertEqual(term("E:.-U:.y.-t.-'").phonetic, "EUyt..")
        self.assertEqual(term("S:.-U:.-'T:.-wa.e.-'t.-x.-s.y.-',").phonetic, "SUTwaetxsy--")
        self.assertEqual(term("t.i.-s.i.-'u.T:.-U:.-'wo.-',S:.-',_").phonetic, "tisiuTUwoS_")
        self.assertEqual(term("f.o.-f.o.-',n.i.-f.i.-',x.-A:.-',_E:A:.-',_;").phonetic, "fofonifixAEA~")

        # d = Dictionary()
        # self.assertEqual(len(set(t.phonetic for t in d)), len(d))