import unittest

from ieml.ieml_objects.parser.parser import IEMLParser
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator, term


class TestPropositionParser(unittest.TestCase):

    def setUp(self):
        self.rand = RandomPoolIEMLObjectGenerator(level=Text)
        self.parser = IEMLParser()

    def test_parse_term(self):
        for i in range(10):
            o = self.rand.term()
            self.assertEqual(self.parser.parse(str(o)), o)

    def test_parse_word(self):
        for i in range(10):
            o = self.rand.word()
            self.assertEqual(self.parser.parse(str(o)), o)

    def test_parse_term_plus(self):
        t = term("f.-O:M:.+M:O:.-s.y.-'")
        to_check = self.parser.parse("[f.-O:M:.+M:O:.-s.y.-']")
        self.assertEqual(to_check, t)

    def test_parse_sentence(self):
        for i in range(10):
            o = self.rand.sentence()
            self.assertEqual(self.parser.parse(str(o)), o)

    def test_parse_super_sentence(self):
        for i in range(10):
            o = self.rand.word()
            self.assertEqual(self.parser.parse(str(o)), o)

    def test_parse_text(self):
        for i in range(10):
            o = self.rand.text()
            self.assertEqual(self.parser.parse(str(o)), o)

    def test_literals(self):
        w1 = str(self.rand.word()) + "<la\la\>lal\>fd>"
        w2 = str(self.rand.word()) + "<@!#$#@%{}\>fd>"
        self.assertEqual(str(self.parser.parse(w1)), w1)
        self.assertEqual(str(self.parser.parse(w2)), w2)
        s1 = '[('+ '*'.join((w1, w2, str(self.rand.word()))) +')]' + "<!@#$%^&*()_+\<>"
        self.assertEqual(str(self.parser.parse(s1)), s1)
        ss1 = '[('+ '*'.join((s1, str(self.rand.sentence()), str(self.rand.sentence()))) + ')]<opopop>'
        self.assertEqual(str(self.parser.parse(ss1)), ss1)

