import random
import unittest
from ieml.dictionary import Dictionary

from ieml.lexicon.grammar import Fact, Theory, Text, Word, Word, Usl, usl, topic
from ieml.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.lexicon.tools import random_usl, replace_paths


class TestTexts(unittest.TestCase):

    #  TODO : more tests on texts
    def setUp(self):
        self.d = Dictionary.load()
        self.rand_gen = RandomPoolIEMLObjectGenerator(self.d, level=Theory)

    def test_text_ordering_simple(self):
        """Just checks that elements created in a text are ordered the right way"""
        topic = self.rand_gen.topic()
        sentence, supersentence = self.rand_gen.fact(), self.rand_gen.theory()
        text = Text([supersentence, sentence, topic])

        self.assertIn(topic, text.words)
        self.assertIn(sentence, text.facts)
        self.assertIn(supersentence, text.theories)

        self.assertTrue(all(isinstance(t, Word) for t in text.semes))
        self.assertTrue(all(isinstance(t, Word) for t in text.words))
        self.assertTrue(all(isinstance(t, Fact) for t in text.facts))
        self.assertTrue(all(isinstance(t, Theory) for t in text.theories))


class TestUsl(unittest.TestCase):
    def test_equality(self):
        ieml = RandomPoolIEMLObjectGenerator(level=Text).text()
        self.assertEqual(usl(ieml), usl(str(ieml)))

    def test_glossary(self):
        txt = random_usl(Text)
        self.assertTrue(all(t.script in Dictionary() for t in txt.semes))
        self.assertTrue(all(t in txt for t in txt.semes))

        with self.assertRaises(ValueError):
            'test' in txt


class TextUslTools(unittest.TestCase):
    def test_replace(self):
        u = topic([usl('[M:]')])
        u2 = replace_paths(u, {'r0': '[S:]'})
        self.assertEqual(u2, topic([usl('[S:]')]))

    def test_deference_path(self):
        u = random_usl(rank_type=Text)
        p = random.sample(tuple(u.paths.items()), 1)
        self.assertEqual(u[p[0][0]], p[0][1])

    def test_translation(self):
        u = random_usl(rank_type=Text)
        t = u.auto_translation()
        self.assertIn('fr', t)
        self.assertIn('en', t)

