import random
import re

from ieml.ieml_objects import RandomPoolIEMLObjectGenerator, Sentence, Hypertext, Text, Word, PropositionPath
from ieml.ieml_objects.hypertexts import Hyperlink
from ieml.ieml_objects.parser.parser import IEMLParser
from ieml.ieml_objects.sentences import SuperSentence
from ieml.paths.tools import resolve
from ieml.usl import usl
from ieml.usl.tools import random_usl, replace_paths
from ieml.usl.usl import Usl
from testing.ieml.helper import *


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

class TextUslToots(unittest.TestCase):
    def test_replace(self):
        u = usl(Word(Morpheme([Term('M:')])))
        u2 = replace_paths(u, [('r0', '[S:]')])
        self.assertEqual(u2, usl(Word(Morpheme([Term('S:')]))))

    def test_deference_path(self):
        u = random_usl(rank_type=Text)
        p = random.sample(tuple(u.paths.items()), 1)
        self.assertEqual(u[p[0][0]], {p[0][1]})
