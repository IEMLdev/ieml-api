import unittest

from ieml.dictionary.terms import Term
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.dictionary import term
from ieml.syntax.tools import proposition
from ieml.tools import ieml
from ieml.syntax import Word, Morpheme


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

    def test_promotion(self):
        self.assertIsInstance(proposition('[A:]'), Word)
        self.assertIsInstance(proposition(term('[A:]')), Word)

        self.assertIsInstance(ieml('[A:]'), Term)
        self.assertIsInstance(ieml(term('[A:]')), Term)

    def test_is_term(self):
        self.assertTrue(proposition('[A:]').is_term)
