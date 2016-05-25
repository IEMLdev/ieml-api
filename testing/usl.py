import unittest

from ieml.AST import RandomPropositionGenerator, Sentence, HyperText, Text, Word, PropositionPath
from ieml.AST.tools import promote_to
from .helper import *


class TestTexts(unittest.TestCase):

    #  TODO : more tests on texts
    def setUp(self):
        self.rand_gen = RandomPropositionGenerator()

    def test_text_ordering_simple(self):
        """Just checks that elements created in a text are ordered the right way"""
        word = self.rand_gen.get_random_proposition(Word)
        sentence, supersentence = promote_to(word, Sentence), promote_to(word, SuperSentence)
        text = Text([supersentence, sentence, word])
        text.check()
        self.assertIsInstance(text.children[0], Word)
        self.assertIsInstance(text.children[1], Sentence)
        self.assertIsInstance(text.children[2], SuperSentence)


class TestHypertext(unittest.TestCase):

    def test_addhyperlink(self):
        """Test if adding an hyperlink trigger a valid recompute"""
        proposition = RandomPropositionGenerator().get_random_proposition(Sentence)
        hypertext = HyperText(Text([proposition]))
        hyperlink = HyperText(Text([RandomPropositionGenerator().get_random_proposition(Word)]))
        hypertext.check()
        hyperlink.check()
        str_first = hypertext._str
        hypertext.add_hyperlink(PropositionPath(proposition=proposition), hyperlink)
        self.assertNotEqual(str_first, hypertext._str)