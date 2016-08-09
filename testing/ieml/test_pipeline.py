from ieml.AST.usl import Text
from ieml.filtering import *
from testing.ieml.helper import *
from models.terms import get_random_terms
from ieml.AST.tools import RandomPropositionGenerator


class BasePipelineTester(unittest.TestCase):

    def setUp(self):
        self.generator = RandomPropositionGenerator()
        self.random_uniterm_words = [self.generator.get_random_uniterm_word() for i in range(10)]
        self.random_multiterm_words = [self.generator.get_random_multiterm_word() for i in range(10)]
        self.random_sentences = [self.generator.get_random_proposition(Sentence) for i in range(3)]


class TestUSLFilteringLevels(BasePipelineTester):
    """Testing how the FilteringLevel Object/Enum behaves, if it assigns the right level to texts"""

    def test_uniterm_level(self):
        text = Text(self.random_uniterm_words)
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.UNITERM_WORD)

    def test_multiterm_level(self):
        text = Text(self.random_multiterm_words + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.MULTITERM_WORD)

    def test_sentence_level(self):
        text = Text(self.random_sentences + self.random_multiterm_words[1:2] + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.SENTENCE)

    def test_supersentence_level(self):
        text = Text([self.generator.get_random_proposition(SuperSentence)] + self.random_sentences +
                    self.random_multiterm_words[1:2] + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.SUPERSENTENCE)

class TestUSLSets(unittest.TestCase):
    """Testing that the USLSet object stores the right objects and orders them properly"""
    pass


class TestPipeLineCreation(unittest.TestCase):
    pass


class TestLinearPipeLine(unittest.TestCase):
    pass


class TestConditionalPipeLine(unittest.TestCase):
    pass
