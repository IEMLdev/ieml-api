import unittest

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.words import Word, Morpheme


class WordsTest(unittest.TestCase):
    def test_create_word(self):
        a = Word(Morpheme([Term('wa.'), Term('we.')]))
        b = Word(Morpheme(reversed([Term('wa.'), Term('we.')])))
        self.assertEqual(a, b)
        self.assertEqual(str(a), str(b))
