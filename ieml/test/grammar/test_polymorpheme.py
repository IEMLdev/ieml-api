import unittest

from ieml.exceptions import CannotParse
from ieml.usl import PolyMorpheme, check_polymorpheme
from ieml.usl.parser import USLParser


class TestPolyMorpheme(unittest.TestCase):
    def test_polymorpheme(self):
        POLYMORPH = [ "U: wo. wa.",
                      "U: m2(wo. wa.)",
                      "m1(U:) m1(S:)",
                      "o. m1(U: S:) m2(t. m.)",
                      "o. m2(A: S: B: T:) m2(y. t.)"
                  ]
        for _t in POLYMORPH:
            t = USLParser().parse(_t)
            assert str(t) == str(_t), "{} != {}".format(str(t), str(_t))
            assert isinstance(t, PolyMorpheme)

            elems = set()
            for ss in t.singular_sequences:
                print(str(ss))
                assert ss.cardinal == 1
                check_polymorpheme(ss)
                assert ss not in elems
                elems.add(ss)


    def test_invalid_cannot_parse_polymorpheme(self):
        POLYMORPH = [
                    "U: wa. m1()",
            #           "m1(wo. wa.)m1(U:)",
                      # "m4(U: S: E: T:)",
                  ]
        for _t in POLYMORPH:
            # assert str(t) == str(_t), "{} != {}".format(str(t), str(_t))
            with self.assertRaises(CannotParse):
                t = USLParser().parse(_t)


    def test_invalid_cannot_check_polymorpheme(self):
        POLYMORPH = ["U: wa. m0(U:)",
                     # "m1(wo. wa.) m1(U:)",
                     "m4(U: S: E: T:)",
                     ]
        for _t in POLYMORPH:
            t = USLParser().parse(_t)
            assert isinstance(t, PolyMorpheme)

            with self.assertRaises(ValueError):
                check_polymorpheme(t)
