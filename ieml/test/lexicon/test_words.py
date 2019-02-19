import unittest

from ieml.lexicon.grammar import usl
from ieml.lexicon.lexicon import Lexicon


class MyTestCase(unittest.TestCase):
    def test_contains(self):
        w = usl("[([S:.E:A:S:.-]+[T:.E:A:S:.-]+[s.-S:.A:.-'+we.f.T:.-+u.A:.-+p.E:A:S:.-+E:T:S:+T:.-'])*([E:])*([E:])]")
        self.assertIn(w, w)

        wss = usl("[([S:.E:A:S:.-]+[T:.E:A:S:.-]+[s.-S:.A:.-'])*([E:])*([E:])]")
        self.assertIn(wss, w)

    def test_lexicon(self):
        for folder in Lexicon.load().names:
            lex = Lexicon.load(names=[folder])
            print(folder)

            paradigms = [u for u in lex.usls if u.cardinal != 1]
            sing = [u for u in lex.usls if u.cardinal == 1]
            for p in paradigms:
                lex.display(p)

            for s in sing:
                for p in paradigms:
                    if s in p:
                        break
                else:
                    lex.display(s)
                    self.fail("Not found in paradigms")


    def test_layers(self):
        w0 = usl("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-']+[b.i.-s.i.-'O:O:.-'E:.-'+s.-T:.O:.-',])*([E:])*([E:])]")
        self.assertEqual(w0.layer, 4)

        w0 = usl("[([E:])*([E:])*([E:])]")
        self.assertEqual(w0.layer, 0)

        w0 = usl("[([A:])*([E:])*([E:])]")
        self.assertEqual(w0.layer, 1)

        w0 = usl("[([E:.A:.g.-])*([A:])*([E:])]")
        self.assertEqual(w0.layer, 2)

        w0 = usl("[([E:.A:.g.-])*([A:])*([U:])]")
        self.assertEqual(w0.layer, 3)
    # [("[([n.-T:.A:.-']+[d.-h.-']+[u.l.-+a.B:.-'+f.-S:.U:.-+T:.A:.-'])*([E:])*([E:])]", )]

    def test_relations(self):
        w0 = usl("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-']+[b.i.-s.i.-'O:O:.-'E:.-'+s.-T:.O:.-',])*([E:])*([E:])]")
        w_p = usl("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-'])*([E:])*([E:])]")
        self.assertIn(w_p, w0.ancestors)

        w_p = usl("[([E:.A:.g.-]+[T:.U:.n.-])*([E:])*([E:])]")
        self.assertIn(w_p, w0.ancestors)

        w_p = usl("[([E:.A:.g.-])*([E:])*([E:])]")
        self.assertIn(w_p, w0.ancestors)

        # w_p = usl("[([E:])*([E:])*([E:])]")
        # self.assertIn(w_p, w0.ancestors)

        self.assertNotIn(w0, w0.ancestors)

        self.assertIn(w0, w0)

        w_in = usl("[([E:.A:.g.-]+[T:.U:.n.-]+[n.-T:.U:.-']+[b.i.-s.i.-'wo.-'s.-T:.U:.-',])*([E:])*([E:])]")
        self.assertIn(w_in, w0)


if __name__ == '__main__':
    unittest.main()
