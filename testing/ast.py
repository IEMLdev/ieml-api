import numpy as np

from ieml.AST.tools import RandomPropositionGenerator, NULL_WORD, NULL_SENTENCE, NULL_SUPERSENTENCE, NULL_CLAUSE, \
    NULL_MORPHEME, NULL_SUPERCLAUSE, promote_to
from ieml.AST.usl import Text, HyperText
from ieml.exceptions import SeveralRootNodeFound, NodeHasTooMuchParents, NoRootNodeFound
from testing.helper import *
from ieml.AST.terms import Term

class TestMetaFeatures(unittest.TestCase):
    """Tests inter-class operations and metaclass related features"""

    def test_class_comparison(self):
        self.assertGreater(Word, Term)
        self.assertGreater(Sentence, Word)
        self.assertLess(Morpheme, SuperSentence)

    def test_precompute_string(self):
        proposition = RandomPropositionGenerator().get_random_proposition(SuperSentence)
        proposition.check()
        self.assertIsNotNone(proposition._str)
        self.assertTrue(proposition.is_checked())
        self.assertTrue(proposition.is_ordered())

        text = Text([proposition])
        text.check()
        self.assertIsNotNone(text._str)
        self.assertTrue(text.is_checked())
        self.assertTrue(text.is_ordered())

        hypertext = HyperText(text)
        hypertext.check()
        self.assertIsNotNone(hypertext._str)
        self.assertTrue(hypertext.is_checked())
        self.assertTrue(hypertext.is_ordered())


class TestPropositionsInclusion(unittest.TestCase):

    def setUp(self):
        self.parser = PropositionsParser()
        self.sentence = self.parser.parse("""[([([h.O:T:.-])]*[([E:O:.T:M:.-])]*[([E:F:.O:O:.-])])+
                                     ([([h.O:T:.-])]*[([wu.T:.-])]*[([h.O:B:.-])])]""")

    def test_word_in_sentence(self):
        word = self.parser.parse("[([h.O:T:.-])]")
        self.assertIn(word, self.sentence)

    def test_term_in_sentence(self):
        term = self.parser.parse("[h.O:T:.-]")
        self.assertIn(term, self.sentence)

    def test_word_not_in_sentence(self):
        word = self.parser.parse("[([wo.S:.-])]")
        self.assertNotIn(word, self.sentence)

class TestTermsFeatures(unittest.TestCase):
    """Checks basic AST features like hashing, ordering for words, morphemes and terms"""

    def setUp(self):
        self.term_a, self.term_b, self.term_c = Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")
        self.term_a.check(), self.term_b.check(), self.term_c.check()

    # def test_term_check(self):
    #     """Tests that a term actually "finds itself" in the database"""
    #     self.assertEqual(self.term_a.objectid, ObjectId("55d220df6653c32453c0ac94"))

    def test_term_check_fail(self):
        term = Term("E:A:T:.wa.wa.-")
        with self.assertRaises(IEMLTermNotFoundInDictionnary):
            term.check()

    def test_terms_equality(self):
        """tests that two different instance of a term are still considered equal once linked against the DB"""
        other_instance = Term("E:A:T:.")
        other_instance.check()
        self.assertEqual(self.term_a, other_instance)
        self.assertFalse(self.term_a is other_instance) # checking they really are two different instances

    def test_terms_comparison(self):
        term_a, term_b = Term("S:M:.e.-M:M:.u.-'+B:M:.e.-M:M:.a.-'+T:M:.e.-M:M:.i.-'"), Term("S:M:.e.-M:M:.u.-'")
        term_b.check(), term_a.check()
        self.assertLess(term_b, term_a)

    def test_term_ordering(self):
        """Checks that terms are properly ordered, through the """
        terms_list = [self.term_b, self.term_a, self.term_c]
        terms_list.sort()
        self.assertEqual(terms_list, [self.term_a, self.term_b, self.term_c])

    def test_term_hashing(self):
        """Checks that terms can be used as keys in a hashmap"""
        hashmap = {self.term_a : 1}
        other_instance = Term("E:A:T:.")
        other_instance.check()
        self.assertTrue(other_instance in hashmap)

    def test_term_sets(self):
        other_a_instance = Term("E:A:T:.")
        other_a_instance.check()
        terms_set = {self.term_b, self.term_a, self.term_c, other_a_instance}
        self.assertEqual(len(terms_set), 3)


class TestMorphemesFeatures(unittest.TestCase):

    def test_morpheme_checks(self):
        """Creates a morpheme with conflicting terms"""
        new_morpheme = Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-"), Term("E:A:T:.")])
        with self.assertRaises(IndistintiveTermsExist):
            new_morpheme.check()

    def _make_and_check_morphemes(self):
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
        morpheme_b = Morpheme([Term("a.i.-"), Term("i.i.-")])
        morpheme_a.check(), morpheme_b.check()
        morpheme_a.order(), morpheme_b.order()
        return morpheme_a, morpheme_b

    def _make_and_check_suffixed_morphemes(self):
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-")])
        morpheme_b = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
        morpheme_a.check(), morpheme_b.check()
        morpheme_a.order(), morpheme_b.order()
        return morpheme_a, morpheme_b

    def test_morpheme_reordering(self):
        """Create a new morpheme with terms in the wrong order, and check that it reorders
        after itself after the reorder() method is ran"""
        new_morpheme = Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")])
        new_morpheme.check()
        self.assertTrue(new_morpheme.is_ordered())
        self.assertEqual(str(new_morpheme.children[2]), '[E:S:.o.-]') # last term is right?

    def test_morpheme_equality(self):
        """Tests if two morphemes That are declared the same way are said to be equal
         using the regular equality comparison. It also tests terms reordering"""
        morpheme_a = Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")])
        morpheme_b = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")])
        morpheme_a.check(), morpheme_b.check()
        morpheme_a.order(), morpheme_b.order()
        self.assertEqual(morpheme_a, morpheme_b)

    def test_morpheme_inequality(self):
        morpheme_a , morpheme_b = self._make_and_check_morphemes()
        self.assertNotEqual(morpheme_a, morpheme_b)

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
        self.word_a.check(), self.word_b.check()
        self.word_a.order(), self.word_b.order()

    def test_words_equality(self):
        """Checks that the == operator works well on words build from the same elements"""
        self.assertEqual(self.word_b, self.word_a)

    def test_words_hashing(self):
        """Verifies words can be used as keys in a hashmap"""
        new_word = Word(Morpheme([Term("E:A:T:."), Term("E:S:.o.-"), Term("E:S:.wa.-")]))
        new_word.check()
        new_word.order()
        word_hashmap = {new_word : 1,
                        self.word_a : 2}
        self.assertTrue(self.word_b in word_hashmap)

    def test_words_with_different_substance_comparison(self):
        word_a,word_b = Word(self.morpheme_a),  Word(self.morpheme_b)
        word_a.check(), word_b.check()
        # true because Term("E:A:T:.") < Term("a.i.-")
        self.assertTrue(word_a < word_b)


class TestClauses(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_comparison(self):
        """Tests the comparison on two clauses not sharing the same substance"""
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b = Clause(a,b,c), Clause(d,e,f)
        clause_a.check(), clause_b.check()
        self.assertTrue(clause_a < clause_b)

    def test_attr_comparison(self):
        """tests the comparison between two clauses sharing the same substance"""
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b = Clause(a,b,c), Clause(a,e,c)
        clause_a.check(), clause_b.check()
        self.assertTrue(clause_a < clause_b)


class TestSentences(unittest.TestCase):

    def test_adjacency_graph_building(self):
        sentence = get_test_sentence()
        adjancency_matrix = np.array([[False,True,True,False,False],
                                      [False,False,False,True,True],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False]])
        self.assertTrue((sentence.graph.adjacency_matrix == adjancency_matrix).all())

    def test_two_many_roots(self):
        a, b, c, d, e, f = tuple(get_words_list())
        sentence = Sentence([Clause(a,b,f), Clause(a,c,f), Clause(b,e,f), Clause(d,b,f)])
        with self.assertRaises(SeveralRootNodeFound):
            sentence.check()

    def test_too_many_parents(self):
        a, b, c, d, e, f = tuple(get_words_list())
        sentence = Sentence([Clause(a,b,f), Clause(a,c,f), Clause(b,e,f), Clause(b,d,f), Clause(c,d,f)])
        with self.assertRaises(NodeHasTooMuchParents):
            sentence.check()

    def test_no_root(self):
        a, b, c, d, e, f = tuple(get_words_list())
        sentence = Sentence([Clause(a,b,f), Clause(b,c,f), Clause(c,a,f), Clause(b,d,f), Clause(c,d,f)])
        with self.assertRaises(NoRootNodeFound):
            sentence.check()

    def test_clause_ordering(self):
        a, b, c, d, e, f = tuple(get_words_list())
        clause_a, clause_b, clause_c, clause_d = Clause(a,b,f), Clause(a,c,f), Clause(b,d,f), Clause(b,e,f)
        sentence = Sentence([clause_a, clause_b, clause_c, clause_d])
        sentence.check()
        self.assertEqual(sentence.children,[clause_a, clause_b,clause_c, clause_d])


class TestSuperSentence(unittest.TestCase):

    def setUp(self):
        self.rnd_gen = RandomPropositionGenerator()

    def test_supersentence_creation(self):
        a, b, c, d, e, f = tuple(self.rnd_gen.get_random_proposition(Sentence) for i in range(6))
        super_sentence = Sentence([SuperClause(a,b,f), SuperClause(a,c,f), SuperClause(b,e,f), SuperClause(b,d,f)])
        try:
            super_sentence.check()
        except Exception as err:
            # self.fail("Super sentence creation failed, error : %s" % str(err))
            raise err


class TestIsNull(unittest.TestCase):

    def setUp(self):
        self.parser = PropositionsParser()

    def test_null_closed_proposition(self):
        NULL_WORD.check(), NULL_SUPERSENTENCE.check(), NULL_SENTENCE.check()
        self.assertTrue(NULL_WORD.is_null)
        self.assertTrue(NULL_SENTENCE.is_null)
        self.assertTrue(NULL_SUPERSENTENCE.is_null)

    def test_null_nonclosed_proposition(self):
        NULL_CLAUSE.check(), NULL_MORPHEME.check(), NULL_SUPERCLAUSE.check()
        self.assertTrue(NULL_CLAUSE.is_null)
        self.assertTrue(NULL_MORPHEME.is_null)
        self.assertTrue(NULL_SUPERCLAUSE.is_null)

    def test_composed_proposition(self):
        promoted_sentence = self.parser.parse("[([([wa.j.-])]*[([E:])]*[([E:])])]")
        self.assertFalse(promoted_sentence.is_null)
        self.assertTrue(promoted_sentence.children[0].mode)


class TestIsPromotion(unittest.TestCase):

    def setUp(self):
        self.parser = PropositionsParser()
        self.rand_gen = RandomPropositionGenerator()

    def test_term_to_sentence_promotion(self):
        promoted_sentence = self.parser.parse("[([([wa.j.-])]*[([E:])]*[([E:])])]")
        term_origin = Term("wa.j.-")
        term_origin.check()
        promotion_origin = promoted_sentence.get_promotion_origin()
        self.assertTrue(promoted_sentence.is_promotion)
        self.assertEqual(promotion_origin, term_origin)

    def test_word_to_sentence_promotion(self):
        rand_word = self.rand_gen.get_random_proposition(Word)
        promoted_sentence = promote_to(rand_word, Sentence)
        self.assertTrue(promoted_sentence.is_promotion)
        self.assertEqual(promoted_sentence.get_promotion_origin(), rand_word)

    def test_word_to_supersentence_promotion(self):
        rand_word = self.rand_gen.get_random_proposition(Word)
        promoted_supersentence = promote_to(rand_word, SuperSentence)
        self.assertTrue(promoted_supersentence.is_promotion)
        self.assertEqual(promoted_supersentence.get_promotion_origin(), rand_word)

    def test_not_a_promotion(self):
        word = self.parser.parse("[([wa.i.-]+[o.]+[O:A:.])*([wa.A:.-])]")
        self.assertFalse(word.is_promotion)

