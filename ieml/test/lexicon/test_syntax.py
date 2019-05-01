import unittest

from ieml.lexicon.grammar.parser2 import IEMLParser
from ieml.lexicon.syntax import Trait, Character, Word


class TestSyntax(unittest.TestCase):
    def test_trait(self):
        _t = "U: wo. wa."
        t = IEMLParser().parse(_t)
        assert str(t) == str(_t)
        assert isinstance(t, Trait)

    def test_character(self):
        TESTS=[
            "[<<U: wo. wa.>> <u. l.> <S:>]",
            "[<<e.>>]",
            "[<u.>]"
        ]
        for _t in TESTS:
            t = IEMLParser().parse(_t)
            assert str(t) == str(_t)
            assert isinstance(t, Character)



    def test_word(self):
        _t = "([<<U: wo. wa.>> <u. l.> <S:>]*[<<e.>>]*[<u.>])"
        t = IEMLParser().parse(_t)
        assert str(t) == str(_t), "Diff " + str(t) + ' original: ' + str(_t)
        assert isinstance(t, Word)