import unittest

from ieml.usl import PolyMorpheme, Word
from ieml.usl.parser import IEMLParser

# TODO: add test for ordering of morph in polymorph

class TestSyntax(unittest.TestCase):
    def test_polymorpheme(self):
        POLYMORPH = [ "U: wo. wa.",
                      "U: m2(wo. wa.)",
                      "m1(U:) m1(S:)",
                      "o. m1(U: S:) m2(t. m.)",
                      "o. m2(A: S: B: T:) m2(y. t.)"
                  ]
        for _t in POLYMORPH:
            t = IEMLParser().parse(_t)
            assert str(t) == str(_t), "{} != {}".format(str(t), str(_t))
            assert isinstance(t, PolyMorpheme)

            elems = set()
            for ss in t.singular_sequences:
                assert ss.cardinal == 1
                ss.check()
                assert ss not in elems
                elems.add(ss)

    def test_word(self):
        CHARACTERS = ["[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-', m1(S: B: T:)) > E:A:. E:A:. ()(k.a.-k.a.-')]",
                      "[! E:S:. (m1(E:.-',b.-S:.U:.-'y.-'U:.-',_ E:.-',b.-S:.U:.-'y.-'A:.-',_))(wa.) > E:.n.- ()(n.i.-s.i.-') > E:.f.- (E:U:S:.)]"]
        for c_str in CHARACTERS:
            c = IEMLParser().parse(c_str)
            assert isinstance(c, Word)

            elems = set()
            for ss in c.singular_sequences:
                assert ss.cardinal == 1
                ss.check()
                assert ss not in elems
                elems.add(ss)
                assert isinstance(ss, Word)


