from ieml.AST.tools import RandomPropositionGenerator
from .helpers import *
from ieml.AST import promote_to
from ieml.exceptions import CannotPromoteToLowerLevel

class TestPromotion(unittest.TestCase):

    def test_promotion(self):
        word = get_test_word_instance()
        word.check()
        sentence = promote_to(word, Sentence)
        self.assertEquals(sentence.__class__, Sentence)
        self.assertEquals(str(sentence), "[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([E:])]*[([E:])])]")

    def test_terms_promotion(self):
        term = Term("E:A:T:.")
        term.check()
        self.assertEquals(str(promote_to(term, Word)), "[([E:A:T:.])]")

    def test_wrong_promotion(self):
        word = get_test_word_instance()
        word.check()
        with self.assertRaises(CannotPromoteToLowerLevel):
            promote_to(word, Morpheme)


class TestRandomGenerator(unittest.TestCase):
    """Kinda don't know what to test for this tool, but if it doesn't raise an execption it's already pretty good"""

    def setUp(self):
        self.generator = RandomPropositionGenerator()

    def test_word_gen(self):
        random_word = self.generator.get_random_proposition(Word)
        try:
            random_word.check()
        except:
            self.fail("Word checking failed")
        self.assertIs(type(random_word), Word)

    def test_sentence_gen(self):
        random_sentence = self.generator.get_random_proposition(Sentence)
        try:
            random_sentence.check()
        except Exception as err:
            self.fail("Sentence checking failed : %s " % err)
        self.assertIs(type(random_sentence), Sentence)