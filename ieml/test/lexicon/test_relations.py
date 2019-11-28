import unittest

from ieml.lexicon.grammar import usl
from ieml.lexicon.lexicon import Lexicon


class TestRelationsTestCase(unittest.TestCase):
    def setUp(self):
        self.lex = Lexicon.load()

    def test_parents(self):
        u = lambda w: self.lex.lattice[w]
        w0 = u("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-']+[b.i.-s.i.-'O:O:.-'E:.-'+s.-T:.O:.-',])*([E:])*([E:])]")
        w_p = u("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-'])*([E:])*([E:])]")

        self.assertIn(w0.word, w_p.child)
        self.assertIn(w_p.word, w0.parents)

        # w_p = u("[([E:.A:.g.-]+[T:.U:.n.-])*([E:])*([E:])]")
        # self.assertIn(w0.word, w_p.child)
        # self.assertIn(w_p.word, w0.parents)
        #
        # w_p = u("[([E:.A:.g.-])*([E:])*([E:])]")
        # self.assertIn(w0.word, w_p.child)
        # self.assertIn(w_p.word, w0.parents)

        # w_p = usl("[([E:])*([E:])*([E:])]")
        # self.assertIn(w_p, w0.ancestors)

        # self.assertIn(w0.word, w0.child)
        #
        # self.assertIn(w0, w0)

        w_in = u("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-']+[b.i.-s.i.-'wo.-'s.-T:.U:.-',])*([E:])*([E:])]")
        self.assertIn(w0.word, w_in.contained_by)
        self.assertIn(w_in.word, w0.contains)

