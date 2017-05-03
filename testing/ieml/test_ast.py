import itertools
import numpy as np

from ieml.ieml_objects import Text, Hypertext, Word, Sentence, SuperSentence, Morpheme, Term
from ieml.ieml_objects.exceptions import TermNotFoundInDictionary, InvalidIEMLObjectArgument
from ieml.ieml_objects.hypertexts import Hyperlink, PropositionPath
from ieml.ieml_objects.parser.parser import IEMLParser
from ieml.ieml_objects.sentences import SuperClause
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator
from ieml.script.operator import sc
from testing.ieml.helper import *


class TestIEMLType(unittest.TestCase):
    def test_rank(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        self.assertEqual(r.term().__class__.rank(), 1)
        self.assertEqual(r.word().__class__.rank(), 3)
        self.assertEqual(r.sentence().__class__.rank(), 5)
        self.assertEqual(r.super_sentence().__class__.rank(), 7)
        self.assertEqual(r.text().__class__.rank(), 8)


# class TestMetaFeatures(unittest.TestCase):
#     """Tests inter-class operations and metaclass related features"""
#
#     def test_class_comparison(self):
#         self.assertGreater(Word, Term)
#         self.assertGreater(Sentence, Word)
#         self.assertLess(Morpheme, SuperSentence)
#
#     def test_precompute_string(self):
#         generator = RandomPoolIEMLObjectGenerator(Text)
#         proposition = generator.sentence()
#
#         self.assertIsNotNone(proposition._str)
#
#         text = Text([proposition])
#         self.assertIsNotNone(text._str)
#
#         hyperlink = Hyperlink(text, generator.text(), PropositionPath((proposition,)))
#         hypertext = Hypertext([hyperlink])
#         self.assertIsNotNone(hypertext._str)

class TestPropositionsInclusion(unittest.TestCase):

    def setUp(self):
        self.parser = IEMLParser()
        self.sentence = self.parser.parse("""[([([h.O:T:.-])]*[([E:O:.T:M:.-])]*[([E:F:.O:O:.-])])+
                                     ([([h.O:T:.-])]*[([wu.T:.-])]*[([h.O:B:.-])])]""")

    def test_word_in_sentence(self):
        word = self.parser.parse("[([h.O:T:.-])]")
        self.assertIn(word, set(itertools.chain.from_iterable(self.sentence)))

    def test_term_in_sentence(self):
        term = self.parser.parse("[h.O:T:.-]")
        self.assertIn(term, set(itertools.chain.from_iterable(itertools.chain.from_iterable(itertools.chain.from_iterable(self.sentence)))))

    def test_word_not_in_sentence(self):
        word = self.parser.parse("[([wo.S:.-])]")
        self.assertNotIn(word, self.sentence)

class TestTermsFeatures(unittest.TestCase):
    """Checks basic AST features like hashing, ordering for words, morphemes and terms"""

    def setUp(self):
        self.term_a, self.term_b, self.term_c = Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")

    # def test_term_check(self):
    #     """Tests that a term actually "finds itself" in the database"""
    #     self.assertEqual(self.term_a.objectid, ObjectId("55d220df6653c32453c0ac94"))

    def test_term_check_fail(self):
        with self.assertRaises(TermNotFoundInDictionary):
            Term("E:A:T:.wa.wa.-")

    def test_terms_equality(self):
        """tests that two different instance of a term are still considered equal once linked against the DB"""
        other_instance = Term("E:A:T:.")
        self.assertTrue(self.term_a == other_instance)
        self.assertFalse(self.term_a is other_instance) # checking they really are two different instances

    def test_terms_comparison(self):
        s_a = sc("S:M:.e.-M:M:.u.-'+B:M:.e.-M:M:.a.-'+T:M:.e.-M:M:.i.-'")
        s_b = sc("S:M:.e.-M:M:.u.-'")
        self.assertLess(s_b, s_a)

    def test_term_ordering(self):
        """Checks that terms are properly ordered, through the """
        terms_list = [self.term_b, self.term_a, self.term_c]
        terms_list.sort()
        self.assertEqual(terms_list, [self.term_a, self.term_b, self.term_c])

    def test_term_hashing(self):
        """Checks that terms can be used as keys in a hashmap"""
        hashmap = {self.term_a : 1}
        other_instance = Term("E:A:T:.")
        self.assertTrue(other_instance in hashmap)

    def test_term_sets(self):
        other_a_instance = Term("E:A:T:.")
        terms_set = {self.term_b, self.term_a, self.term_c, other_a_instance}
        self.assertEqual(len(terms_set), 3)


class TestMorphemesFeatures(unittest.TestCase):

    def test_morpheme_checks(self):
        """Creates a morpheme with conflicting terms"""
        with self.assertRaises(InvalidIEMLObjectArgument):
            Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-"), Term("E:A:T:.")])

    def _make_and_check_morphemes(self):
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
        morpheme_b = Morpheme([Term("a.i.-"), Term("i.i.-")])
        return morpheme_a, morpheme_b

    def _make_and_check_suffixed_morphemes(self):
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-")])
        morpheme_b = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
        return morpheme_a, morpheme_b

    def test_morpheme_reordering(self):
        """Create a new morpheme with terms in the wrong order, and check that it reorders
        after itself after the reorder() method is ran"""
        new_morpheme = Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")])
        self.assertEqual(str(new_morpheme.children[2]), '[E:S:.o.-]') # last term is right?

    def test_morpheme_equality(self):
        """Tests if two morphemes That are declared the same way are said to be equal
         using the regular equality comparison. It also tests terms reordering"""
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")])
        morpheme_b = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")])
        self.assertTrue(morpheme_a == morpheme_b)

    def test_morpheme_inequality(self):
        morpheme_a , morpheme_b = self._make_and_check_morphemes()
        self.assertTrue(morpheme_a != morpheme_b)

    def test_different_morpheme_comparison(self):
        morpheme_a, morpheme_b = self._make_and_check_morphemes()
        # true because Term("E:A:T:.") < Term("a.i.-")
        self.assertTrue(morpheme_b > morpheme_a)

    def test_suffixed_morpheme_comparison(self):
        morpheme_a, morpheme_b = self._make_and_check_suffixed_morphemes()
        # true since morph_a suffix of morph_b
        self.assertTrue(morpheme_b > morpheme_a)


class TestWords(unittest.TestCase):

    def setUp(self):
        self.morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
        self.morpheme_b = Morpheme([Term("a.i.-"), Term("i.i.-")])
        self.word_a = Word(self.morpheme_a, self.morpheme_b)
        self.word_b = Word(Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")]),
                          Morpheme([Term("a.i.-"), Term("i.i.-")]))

    def test_words_equality(self):
        """Checks that the == operator works well on words build from the same elements"""
        self.assertTrue(self.word_b == self.word_a)

    def test_words_hashing(self):
        """Verifies words can be used as keys in a hashmap"""
        new_word = Word(Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")]))
        word_hashmap = {new_word : 1,
                        self.word_a : 2}
        self.assertTrue(self.word_b in word_hashmap)

    def test_words_with_different_substance_comparison(self):
        word_a,word_b = Word(self.morpheme_a),  Word(self.morpheme_b)
        # true because Term("E:A:T:.") < Term("a.i.-")
        self.assertTrue(word_a < word_b)


class TestClauses(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_comparison(self):
        """Tests the comparison on two clauses not sharing the same substance"""
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b = Clause(a,b,c), Clause(d,e,f)
        self.assertTrue(clause_a < clause_b)

    def test_attr_comparison(self):
        """tests the comparison between two clauses sharing the same substance"""
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b = Clause(a,b,c), Clause(a,e,c)
        self.assertTrue(clause_a < clause_b)


class TestSentences(unittest.TestCase):

    def test_adjacency_graph_building(self):
        sentence = get_test_sentence()
        adjancency_matrix = np.array([[False,True,True,False,False],
                                      [False,False,False,True,True],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False]])
        self.assertTrue((sentence.tree_graph.array == adjancency_matrix).all())

    def test_two_many_roots(self):
        a, b, c, d, e, f = tuple(get_words_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            Sentence([Clause(a, b, f), Clause(a, c, f), Clause(b, e, f), Clause(d, b, f)])

    def test_too_many_parents(self):
        a, b, c, d, e, f = tuple(get_words_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            Sentence([Clause(a, b, f), Clause(a, c, f), Clause(b, e, f), Clause(b, d, f), Clause(c, d, f)])

    def test_no_root(self):
        a, b, c, d, e, f = tuple(get_words_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            Sentence([Clause(a, b, f), Clause(b, c, f), Clause(c, a, f), Clause(b, d, f), Clause(c, d, f)])

    def test_clause_ordering(self):
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b, clause_c, clause_d = Clause(a,b,f), Clause(a,c,f), Clause(b,d,f), Clause(b,e,f)
        sentence = Sentence([clause_a, clause_b, clause_c, clause_d])
        self.assertEqual(sentence.children, (clause_a, clause_b,clause_c, clause_d))


class TestSuperSentence(unittest.TestCase):

    def setUp(self):
        self.rnd_gen = RandomPoolIEMLObjectGenerator(Sentence)

    def test_supersentence_creation(self):
        a, b, c, d, e, f = tuple(self.rnd_gen.sentence() for i in range(6))
        try:
            super_sentence = SuperSentence([SuperClause(a,b,f), SuperClause(a,c,f), SuperClause(b,e,f), SuperClause(b,d,f)])
        except InvalidIEMLObjectArgument as e:
            self.fail()
#
# class TestIsPromotion(unittest.TestCase):
#
#     def setUp(self):
#         self.parser = IEMLParser()
#         self.rand_gen = RandomPropositionGenerator()
#
#     def test_term_to_sentence_promotion(self):
#         promoted_sentence = self.parser.parse("[([([wa.j.-])]*[([E:])]*[([E:])])]")
#         term_origin = Term("wa.j.-")
#         promotion_origin = promoted_sentence.get_promotion_origin()
#         self.assertTrue(promoted_sentence.is_promotion)
#         self.assertEqual(promotion_origin, term_origin)
#
#     def test_word_to_sentence_promotion(self):
#         rand_word = self.rand_gen.get_random_proposition(Word)
#         promoted_sentence = promote_to(rand_word, Sentence)
#         self.assertTrue(promoted_sentence.is_promotion)
#         self.assertEqual(promoted_sentence.get_promotion_origin(), rand_word)
#
#     def test_word_to_supersentence_promotion(self):
#         rand_word = self.rand_gen.get_random_proposition(Word)
#         promoted_supersentence = promote_to(rand_word, SuperSentence)
#         self.assertTrue(promoted_supersentence.is_promotion)
#         self.assertEqual(promoted_supersentence.get_promotion_origin(), rand_word)
#
#     def test_not_a_promotion(self):
#         word = self.parser.parse("[([wa.i.-]+[o.]+[O:A:.])*([wa.A:.-])]")
#         self.assertFalse(word.is_promotion)
#
