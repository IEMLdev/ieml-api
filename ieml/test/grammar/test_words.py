import unittest

# from ieml.dictionary.terms import Term
from ieml.lexicon.grammar import usl

from ieml.exceptions import InvalidIEMLObjectArgument, CannotParse
# from ieml.dictionary import term
# from ieml.lexicon import topic, Word, usl, Topic
from ieml.lexicon.grammar import Word


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

    def test_parse(self):
        word = "[([l.-T:.U:.-',n.-T:.A:.-',d.-S:.U:.-',_+E:.-U:.s.-l.-'+n.i.-d.i.-t.u.-'+wo.f.A:.-+wu.f.S:.-'+s.-S:+T:.A:.-',_])*([E:])*([E:])]"
        u = usl(word)
        self.assertIsInstance(u, Word)
        word = "[([l.-T:.U:.-',n.-T:.A:.-',d.-S:.U:.-',_+E:.-U:.s.-l.-'+n.i.-d.i.-t.u.-'+wo.f.A:.-+wu.f.S:.-'+s.-S:+T:.A:.-',_])*([E:])*([E:])]"
        u = usl(word)
        self.assertIsInstance(u, Word)