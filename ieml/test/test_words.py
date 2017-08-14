import unittest

from ieml.dictionary.terms import Term
from ieml.exceptions import InvalidIEMLObjectArgument, CannotParse
from ieml.dictionary import term
from ieml.syntax.terms import SyntaxTerm
from ieml.tools import ieml
from ieml.syntax import Word, Morpheme


class WordsTest(unittest.TestCase):
    def test_create_word(self):
        a = Word(Morpheme([ieml('[wa.]'), ieml('[we.]')]))
        b = Word(Morpheme(reversed([ieml('[wa.]'), ieml('[we.]')])))
        self.assertEqual(a, b)
        self.assertEqual(str(a), str(b))

    def test_word_instanciation(self):
        with self.assertRaises(CannotParse):
            # "Too many singular sequences"
            ieml("[([O:M:.]+[wa.]+[M:M:.])*([O:O:.M:O:.-])]")

    def test_promotion(self):
        self.assertIsInstance(Word.from_term(ieml('[A:]')), Word)
        self.assertIsInstance(Word.from_term(term('[A:]')), Word)

        self.assertIsInstance(ieml('[A:]'), SyntaxTerm)
        self.assertIsInstance(ieml(term('[A:]')), SyntaxTerm)

    def test_is_term(self):
        self.assertTrue(Word.from_term(ieml('[A:]')).is_term)
