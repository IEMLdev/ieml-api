import unittest

from ieml.dictionary.terms import Term
from ieml.exceptions import InvalidIEMLObjectArgument, CannotParse
from ieml.dictionary import term
from ieml.grammar import topic, Word, usl, Topic


class TopicsTest(unittest.TestCase):
    def test_create_topic(self):
        a = topic([usl('[wa.]'), usl('[we.]')])
        b = topic(reversed([usl('[wa.]'), usl('[we.]')]))
        self.assertEqual(a, b)
        self.assertEqual(str(a), str(b))

    def test_word_instanciation(self):
        with self.assertRaises(CannotParse):
            # "Too many singular sequences"
            usl("[([O:M:.]+[wa.]+[M:M:.])*([O:O:.M:O:.-])]")

    def test_promotion(self):
        self.assertIsInstance(usl('[A:]'), Word)
        self.assertIsInstance(topic(['[A:]']), Topic)

        self.assertIsInstance(term('[A:]'), Term)
