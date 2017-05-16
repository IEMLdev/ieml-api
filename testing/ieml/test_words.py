import unittest

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.ieml_objects.words import Word, Morpheme


class WordsTest(unittest.TestCase):
    def test_create_word(self):
        a = Word(Morpheme([Term('wa.'), Term('we.')]))
        b = Word(Morpheme(reversed([Term('wa.'), Term('we.')])))
        self.assertEqual(a, b)
        self.assertEqual(str(a), str(b))

    def test_word_instanciation(self):
        words = [RandomPoolIEMLObjectGenerator().word() for _ in range(10)]

        with self.assertRaises(ValueError):
            # "Too many singular sequences"
            ieml("[([O:M:.]+[wa.]+[M:M:.])*([O:O:.M:O:.-])]")

