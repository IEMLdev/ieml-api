import random
import unittest

import numpy as np

from ieml.lexicon import Fact, Theory, Text, theory, text, topic
from ieml.exceptions import InvalidIEMLObjectArgument, TermNotFoundInDictionary
from ieml.lexicon.parser import IEMLParser
from ieml.tools import RandomPoolIEMLObjectGenerator
from ieml.dictionary.script import script as sc
from ieml.test.helper import *

class TestIEMLType(unittest.TestCase):
    def test_rank(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        self.assertEqual(r.word().__class__.syntax_rank(), 1)
        self.assertEqual(r.topic().__class__.syntax_rank(), 2)
        self.assertEqual(r.fact().__class__.syntax_rank(), 3)
        self.assertEqual(r.theory().__class__.syntax_rank(), 4)
        self.assertEqual(r.text().__class__.syntax_rank(), 5)


class TestPropositionsInclusion(unittest.TestCase):

    def setUp(self):
        self.parser = IEMLParser()
        self.sentence = self.parser.parse("""[([([h.O:T:.-])]*[([E:.-O:.T:M:.-l.-'])]*[([E:.F:.O:O:.-])])+
                                     ([([h.O:T:.-])]*[([s.wu.T:.-])]*[([h.O:B:.-])])]""")

    def test_word_in_sentence(self):
        word = self.parser.parse("[([h.O:T:.-])]")
        self.assertIn(word, self.sentence)

    def test_term_in_sentence(self):
        term = self.parser.parse("[h.O:T:.-]")
        self.assertIn(term, self.sentence)

    def test_word_not_in_sentence(self):
        word = self.parser.parse("[([s.wo.S:.-])]")
        self.assertNotIn(word, self.sentence)

class TesttermsFeatures(unittest.TestCase):
    """Checks basic AST features like hashing, ordering for words, morphemes and terms"""

    def setUp(self):
        self.term_a, self.term_b, self.term_c = term("E:A:T:."), term("E:.S:.wa.-"), term("E:.-S:.o.-t.-'")

    def test_term_check_fail(self):
        with self.assertRaises(TermNotFoundInDictionary):
            term("E:A:T:.wa.wa.-")

    def test_terms_equality(self):
        """tests that two different instance of a term are still considered equal once linked against the DB"""
        other_instance = term("E:A:T:.")
        self.assertTrue(self.term_a == other_instance)
        self.assertTrue(self.term_a is other_instance) # checking they really are two different instances

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
        other_instance = term("E:A:T:.")
        self.assertTrue(other_instance in hashmap)

    def test_term_sets(self):
        other_a_instance = term("E:A:T:.")
        terms_set = {self.term_b, self.term_a, self.term_c, other_a_instance}
        self.assertEqual(len(terms_set), 3)

class TestWords(unittest.TestCase):

    def test_word_instanciation(self):
        w = word("U:")
        self.assertEqual(w, word('U:', literals=str(random.randint(0, 1000000000))))

    def test_update_literal(self):
        w = word("U:")
        w1 = word(w, literals="test")
        self.assertEqual(w1.literals, ("test",))
        self.assertEqual(w1.literals, word(w1).literals)

class TestTopics(unittest.TestCase):

    def setUp(self):
        self.morpheme_a = [term("E:A:T:."), term("E:.S:.wa.-"),term("E:.-S:.o.-t.-'")]
        self.morpheme_b = [term("a.i.-"), term("i.i.-")]
        self.word_a = topic(self.morpheme_a, self.morpheme_b)
        self.word_b = topic([term("E:A:T:."), term("E:.-S:.o.-t.-'"), term("E:.S:.wa.-")],
                           [term("a.i.-"), term("i.i.-")])

    def test_topics_equality(self):
        """Checks that the == operator works well on words build from the same elements"""
        self.assertTrue(self.word_b == self.word_a)

    def test_topics_hashing(self):
        """Verifies words can be used as keys in a hashmap"""
        new_word = topic([term("E:A:T:."), term("E:.-S:.o.-t.-'"), term("E:.S:.wa.-")])
        word_hashmap = {new_word : 1,
                        self.word_a : 2}
        self.assertTrue(self.word_b in word_hashmap)

    def test_topics_with_different_substance_comparison(self):
        word_a,word_b = topic(self.morpheme_a),  topic(self.morpheme_b)
        # true because term("E:A:T:.") < term("a.i.-")
        self.assertTrue(word_a < word_b)

    def test_topics_reordering(self):
        morpheme_a = [term("E:A:T:."), term("E:.-S:.o.-t.-'"), term("E:.S:.wa.-")]
        morpheme_b = [term("E:A:T:."), term("E:.S:.wa.-"), term("E:.-S:.o.-t.-'")]
        self.assertTrue(topic(morpheme_a) == topic(morpheme_b))

class TestClauses(unittest.TestCase):

    def test_simple_comparison(self):
        """Tests the comparison on two clauses not sharing the same substance"""
        a, b, c, d, e, f = tuple(get_topics_list())
        clause_a, clause_b = (a,b,c), (d,e,f)
        self.assertTrue(clause_a < clause_b)

    def test_attr_comparison(self):
        """tests the comparison between two clauses sharing the same substance"""
        a, b, c, d, e, f = tuple(get_topics_list())
        clause_a, clause_b = (a,b,c), (a,e,c)
        self.assertTrue(clause_a < clause_b)

    def test_hashing(self):
        a, b, c, d, e, f = tuple(get_topics_list())
        clause_a, clause_b = (a,b,c), (a,e,c)
        h = {clause_a: 1,
             clause_b: 3}
        self.assertIn(clause_a, h)



class TestFacts(unittest.TestCase):

    def test_adjacency_graph_building(self):
        sentence = get_test_sentence()
        adjancency_matrix = np.array([[False,True,False,False,True],
                                      [False,False,True,True,False],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False],
                                      [False,False,False,False,False]])
        self.assertTrue((sentence.tree_graph.array == adjancency_matrix).all())

    def test_two_many_roots(self):
        a, b, c, d, e, f = tuple(get_topics_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            fact([(a, b, f), (a, c, f), (b, e, f), (d, b, f)])

    def test_too_many_parents(self):
        a, b, c, d, e, f = tuple(get_topics_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            fact([(a, b, f), (a, c, f), (b, e, f), (b, d, f), (c, d, f)])

    def test_no_root(self):
        a, b, c, d, e, f = tuple(get_topics_list())
        with self.assertRaises(InvalidIEMLObjectArgument):
            fact([(a, b, f), (b, c, f), (c, a, f), (b, d, f), (c, d, f)])

    def test_clause_ordering(self):
        a, b, c, d, e, f = tuple(get_topics_list())
        clause_a, clause_b, clause_c, clause_d = (a,b,f), (a,c,f), (b,d,f), (b,e,f)
        sentence = fact([clause_a, clause_b, clause_c, clause_d])
        self.assertEqual(sentence.children, (clause_a, clause_b,clause_c, clause_d))

    def test_hashing(self):
        s = RandomPoolIEMLObjectGenerator(level=Fact).fact()
        h = {s: 1,
             2:3}
        self.assertIn(s, h)


class TestTheory(unittest.TestCase):

    def setUp(self):
        self.rnd_gen = RandomPoolIEMLObjectGenerator(Fact)

    def test_theory_creation(self):
        a, b, c, d, e, f = tuple(self.rnd_gen.fact() for _ in range(6))
        try:
            theory([(a,b,f), (a,c,f), (b,e,f), (b,d,f)])
        except InvalidIEMLObjectArgument as e:
            self.fail()

    def test_hashing(self):
        s = RandomPoolIEMLObjectGenerator(level=Theory).theory()
        h = {s: 1,
             2:3}
        self.assertIn(s, h)


class TestText(unittest.TestCase):
    def setUp(self):
        self.gen = RandomPoolIEMLObjectGenerator(Text)

    def test_equality(self):
        text0 = self.gen.text()
        self.assertEqual(text0, Text(text0))

        s0 = self.gen.fact()
        t1 = text([text0, s0])
        self.assertIn(s0, t1)
        self.assertIn(text0, t1)

    def test_hashing(self):
        s = RandomPoolIEMLObjectGenerator(level=Text).text()
        h = {s: 1,
             2:3}
        self.assertIn(s, h)