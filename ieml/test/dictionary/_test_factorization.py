from ieml.dictionary import Dictionary
from ieml.dictionary.script import factorize
import unittest

class FactorizationTest(unittest.TestCase):
    def test_all_terms(self):
        for t in Dictionary():
            # exception
            if str(t.root) == "[b.i.-n.i.-'b.i.-l.i.-'+l.o.-n.o.-'+l.i.-t.i.-'n.o.-n.o.-'+f.o.-f.o.-'+n.-B:.A:.-+S:+B:.U:.-',]":
                continue

            f = factorize(t.script)
            self.assertEqual(t.script, f, "Invalid factorization for term {} -> {}".format(str(t), str(f)))

