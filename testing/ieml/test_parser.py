import unittest

from ieml.ieml_objects.parser.parser import IEMLParser
from ieml.ieml_objects.sentences import Sentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.words import Morpheme, Word
# from ieml.object.tools import RandomPropositionGenerator
# from testing.ieml.helper import *


class TestPropositionParser(unittest.TestCase):

    def setUp(self):
        self.morpheme_subst = Morpheme([Term("a.i.-"), Term("i.i.-")])
        self.morpheme_mode = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")])
        self.word_object = Word(self.morpheme_subst, self.morpheme_mode)
        self.parser = IEMLParser()

    def test_parse_morpheme(self):
        with open("../../data/example_morpheme.txt") as ieml_file:
            morpheme_ast = self.parser.parse(ieml_file.read())
        self.assertEqual(morpheme_ast, self.morpheme_mode)

    def test_parse_word(self):
        with open("../../data/example_word.txt") as ieml_file:
            word_ast = self.parser.parse(ieml_file.read())
        self.assertEqual(word_ast, self.word_object)

    def test_parse_term_plus(self):
        term = Term("f.-O:M:.+M:O:.-s.y.-'")
        to_check = self.parser.parse("[f.-O:M:.+M:O:.-s.y.-']")
        self.assertEqual(to_check, term)

    def test_ordering(self):
        supersentence_ast = self.parser.parse(str(RandomPropositionGenerator().get_random_proposition(SuperSentence)))
        self.assertTrue(supersentence_ast.is_ordered())
        self.assertTrue(supersentence_ast.is_checked())


class TestUSLParser(unittest.TestCase):

    def setUp(self):
        self.parser = IEMLParser()

    def test_text(self):
        """Weak test of the USL with hyperlink parsing"""
        with open("../../data/example_text.txt") as ieml_file:
            usl_obj = self.parser.parse(ieml_file.read())
        self.assertEqual(len(usl_obj.children), 2)

    def test_with_hyperlink(self):
        """Weak test of the USL with hyperlink parsing"""
        with open("../../data/example_usl_one_hyperlink.txt") as ieml_file:
            usl_obj = self.parser.parse(ieml_file.read())
        self.assertEqual(len(usl_obj.children), 1)

        self.assertEqual(set(type(child) for child in usl_obj.children[0].children[0].children), {Word, Sentence})

    def test_with_multiple_hyperlinks(self):
        """Weak test of the USL with hyperlink parsing"""
        with open("../../data/example_usl_multiple_hyperlinks.txt") as ieml_file:
            usl_obj = self.parser.parse(ieml_file.read())
        self.assertEqual(len(usl_obj.children), 3)
