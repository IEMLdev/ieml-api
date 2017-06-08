import unittest

from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument
from ieml.ieml_objects.terms import term
from ieml.ieml_objects.tools import ieml
from ieml.ieml_objects.words import Word, Morpheme


class WordsTest(unittest.TestCase):
    def test_create_word(self):
        a = Word(Morpheme([term('wa.'), term('we.')]))
        b = Word(Morpheme(reversed([term('wa.'), term('we.')])))
        self.assertEqual(a, b)
        self.assertEqual(str(a), str(b))

    def test_word_instanciation(self):
        with self.assertRaises(InvalidIEMLObjectArgument):
            # "Too many singular sequences"
            ieml("[([O:M:.]+[wa.]+[M:M:.])*([O:O:.M:O:.-])]")

