from ieml.AST import promote_to, Term
from ieml.AST.tools import RandomPropositionGenerator, demote_once
from ieml.exceptions import CannotPromoteToLowerLevel
from .helper import *


class TestPromotion(unittest.TestCase):

    def test_promotion(self):
        word = get_test_word_instance()
        word.check()
        sentence = promote_to(word, Sentence)
        self.assertEqual(sentence.__class__, Sentence)
        self.assertEqual(str(sentence), "[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([E:])]*[([E:])])]")

    def test_terms_promotion(self):
        term = Term("E:A:T:.")
        term.check()
        self.assertEqual(str(promote_to(term, Word)), "[([E:A:T:.])]")

    def test_wrong_promotion(self):
        word = get_test_word_instance()
        word.check()
        with self.assertRaises(CannotPromoteToLowerLevel):
            promote_to(word, Morpheme)


class TestDemotion(unittest.TestCase):

    def setUp(self):
        self.rand_gen = RandomPropositionGenerator()

    def test_single_demotion(self):
        word = self.rand_gen.get_random_proposition(Word)
        superclause = self.rand_gen.get_random_proposition(SuperClause)
        self.assertIsInstance(demote_once(word), Morpheme)
        self.assertIsInstance(demote_once(superclause), Sentence)

    # TODO : Do more of the demotions test


class TestPathPathComputation(unittest.TestCase):

    def setUp(self):
        self.parser = PropositionsParser()

    def test_word_in_sentence_path(self):
        sentence = self.parser.parse("""[([([h.O:T:.-])]*[([E:O:.T:M:.-])]*[([E:F:.O:O:.-])])+
            ([([h.O:T:.-])]*[([wu.T:.-])]*[([h.O:B:.-])])]""")
        word = self.parser.parse("[([h.O:T:.-])]")
        self.assertListEqual(compute_path_between_propositions(sentence, word), [str(sentence), ])


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
        for i in range(20):
            random_sentence = self.generator.get_random_proposition(Sentence)
            try:
                random_sentence.check()
            except Exception as err:
                self.fail("%s checking failed : %s " % (str(random_sentence), str(err)))

    def test_proposition_gen(self):
        for prop_type in [Morpheme, Word, Sentence, Clause, SuperSentence, SuperClause]:
            with self.subTest("Random %s generation failed" % str(prop_type)):
                random_proposition = self.generator.get_random_proposition(prop_type)
                try:
                    random_proposition.check()
                except Exception as err:
                    print(random_proposition.__class__)
                    # self.fail("%s checking failed : %s " % (str(prop_type), str(err)))
                    raise err
                self.assertIs(type(random_proposition), prop_type)