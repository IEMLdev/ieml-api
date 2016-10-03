from ieml.ieml_objects import RandomPoolIEMLObjectGenerator, Sentence, Hypertext, Text, Word, PropositionPath
from ieml.ieml_objects.hypertexts import Hyperlink
from ieml.ieml_objects.sentences import SuperSentence
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


class TestHypertext(unittest.TestCase):

    def test_addhyperlink(self):
        """Test if adding an hyperlink trigger a valid recompute"""
        pool = RandomPoolIEMLObjectGenerator(level=Sentence)
        proposition = pool.sentence()
        text1 = Text([proposition])
        text2 = Text([pool.word()])
        hypertext = Hypertext([Hyperlink(text1, text2, PropositionPath([proposition]))])

        self.assertNotEqual(str(text1), hypertext._str)
        self.assertNotEqual(str(text2), hypertext._str)
