import random
import unittest
from ieml.dictionary import Dictionary

from ieml.syntax import Sentence, Text, Word, SuperSentence
from ieml.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.usl import usl, Usl
from ieml.usl.tools import random_usl, replace_paths
from ieml.test.helper import *


class TestTexts(unittest.TestCase):

    #  TODO : more tests on texts
    def setUp(self):
        self.rand_gen = RandomPoolIEMLObjectGenerator(level=SuperSentence)

    def test_text_ordering_simple(self):
        """Just checks that elements created in a text are ordered the right way"""
        word = self.rand_gen.word()
        sentence, supersentence = self.rand_gen.sentence(), self.rand_gen.super_sentence()
        text = Text([supersentence, sentence, word])

        self.assertIsInstance(text.children[0], Word)
        self.assertIsInstance(text.children[1], Sentence)
        self.assertIsInstance(text.children[2], SuperSentence)


# class TestHypertext(unittest.TestCase):
#
#     def test_addhyperlink(self):
#         """Test if adding an hyperlink trigger a valid recompute"""
#         pool = RandomPoolIEMLObjectGenerator(level=Sentence)
#         proposition = Word(Morpheme([pool.term()]))
#         text2 = Text([Word(Morpheme([pool.term()]))])
#         text1 = Text([proposition])
#         hypertext = Hypertext([Hyperlink(text1, text2, PropositionPath([proposition]))])
#
#         self.assertNotEqual(str(text1), hypertext._str)
#         self.assertNotEqual(str(text2), hypertext._str)
#
#     def test_parse_hypertext(self):
#         hype_str = "{/[([o.wa.-])]{/[([t.i.-s.i.-'])]/}/}"
#         self.assertEqual(str(IEMLParser().parse(hype_str)), hype_str)

class TestUsl(unittest.TestCase):
    def test_equality(self):
        ieml = RandomPoolIEMLObjectGenerator(level=Text).text()
        self.assertEqual(Usl(ieml_object=ieml), Usl(ieml_object=ieml))

    def test_glossary(self):
        txt = random_usl(Text)
        self.assertTrue(all(t in Dictionary() for t in txt.glossary))
        self.assertTrue(all(t in txt for t in txt.glossary))

        with self.assertRaises(ValueError):
            'test' in txt


class TextUslTools(unittest.TestCase):
    def test_replace(self):
        u = usl(Word(Morpheme([ieml('[M:]')])))
        u2 = replace_paths(u, {'r0': '[S:]'})
        self.assertEqual(u2, usl(Word(Morpheme([ieml('[S:]')]))))

    def test_deference_path(self):
        u = random_usl(rank_type=Text)
        p = random.sample(tuple(u.paths.items()), 1)
        self.assertEqual(u[p[0][0]], p[0][1])

    def test_translation(self):
        u = random_usl(rank_type=Text)
        t = u.auto_translation()
        self.assertIn('fr', t)
        self.assertIn('en', t)
