import unittest

from ieml.lexicon.grammar.parser2 import IEMLParser
from ieml.lexicon.syntax import Trait, Character, Word, check_character, check_trait


class TestSyntax(unittest.TestCase):
    def test_trait(self):
        TRAITS = ["<<U: wo. wa.>>",
                  "<<U: m2(wo. wa.)>>",
                  "<<m1(U:)> m1(S:)>",
                  "<<m1(U: S:) m2(m. t.)> o.>",
                  "<<o. m2(t. y.)> m2(A: B: S: T:)>"
                  ]
        for _t in TRAITS:
            t = IEMLParser().parse(_t)
            assert str(t) == str(_t), "{} != {}".format(str(t), str(_t))
            assert isinstance(t, Trait)

            elems = set()
            for ss in t.singular_sequences:
                print(str(ss))
                assert ss.cardinal == 1
                check_trait(ss)
                assert ss not in elems
                elems.add(ss)

    def test_singular_sequences(self):
        CHARACTERS = ["[<E:.wo.-> <<U: wo. m1(m. y. l.)> u. l.> <<U: m2(wo. wa.)>>]",
                      "[<E:.wo.-> <<m3(wo. wa. we. wu.) m1(m. y. l.)> m3(wo. wa. we. wu.) m1(m. y. l.)>]"]
        for c_str in CHARACTERS:
            c = IEMLParser().parse(c_str)
            elems = set()
            for ss in c.singular_sequences:
                print(str(ss))
                assert ss.cardinal == 1
                check_character(ss)
                assert ss not in elems
                elems.add(ss)



    def test_character(self):
        TESTS=[
            "[<E:.wo.-> <<U: wo. wa.> u. l.> <<U: m2(wo. wa.)>>]",
            "[<E:.wo.-> <<e.>>]",
            "[<E:.wo.-> <<u.>>]",
        ]
        for _t in TESTS:
            t = IEMLParser().parse(_t)
            assert str(t) == str(_t)
            assert isinstance(t, Character)

        INVALID=["[<E:> <<U:>>]"]

    def test_word(self):
        _t = "([<E:.wo.-> <<U: wo. wa.>> <<S:>> <<u. l.>>]*[<E:>]*[<E:.wo.-> <<u.>>])"
        t = IEMLParser().parse(_t)
        assert str(t) == str(_t), "Diff " + str(t) + ' original: ' + str(_t)
        assert isinstance(t, Word)


    # def test_word(self):
    #     _t = "([<E:.wo.-> <<U: wo. wa.>> <<S:>> <<u. l.>>]*[<E:>]*[<E:.wo.-> <<u.>>])"
    #     t = IEMLParser().parse(_t)
    #     assert str(t) == str(_t), "Diff " + str(t) + ' original: ' + str(_t)
    #     assert isinstance(t, Word)