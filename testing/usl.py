import unittest

from ieml.AST import RandomPropositionGenerator, Sentence, HyperText, Text, Word, PropositionPath
from .helper import *


class TestTexts(unittest.TestCase):

    def test_text_to_str(self):
        pass


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