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

    def test_wrong_promotion(self):
        word = get_test_word_instance()
        word.check()
        with self.assertRaises(CannotPromoteToLowerLevel):
            promote_to(word, Morpheme)