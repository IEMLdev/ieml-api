import random
from unittest.case import TestCase

from ieml.exceptions import InvalidPathException
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator, replace_from_paths
from ieml.ieml_objects.words import Word
from ieml.script.operator import sc
from ieml.usl.tools import random_usl
from ieml.usl.usl import Usl


class TestTreeStructure(TestCase):
    def test_path(self):
        text = RandomPoolIEMLObjectGenerator(level=Text).text()
        with self.assertRaises(InvalidPathException):
            text.path([Term('wa.')])

        path = []
        c = text
        while not isinstance(c, Term):
            c = c.children[random.randint(0, len(c.children) - 1)]
            path.append(c)

        c2 = Term(c.script)

        self.assertEqual(text.path(path), c2)

    def test_equal(self):
        t = RandomPoolIEMLObjectGenerator(level=Text).text()
        t2 = Text(children=t.children)
        self.assertNotEqual(id(t), id(t2))
        self.assertEqual(t, t2)

        self.assertEqual(t, str(t))
        self.assertEqual(str(t), t)

    def test_replace(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        text = r.text()

        c0 = r.word()
        while text.children[0] == c0:
            c0 = r.word()

        text2 = replace_from_paths(text, [[text.children[0]]], [c0])
        self.assertTrue(c0 in text2)
        self.assertNotEqual(text2, text)

        t = Term('wa.')
        self.assertEqual(replace_from_paths(t, [[sc('wa.')]], [sc('we.')]), t)

        with self.assertRaises(ValueError):
            replace_from_paths(t, [], [Term])

        t2 = Term('we.')
        self.assertEqual(t2, replace_from_paths(t, [[]], [t2]))

        #TODO multiple path

    def _get_child(self):
        pass


class TestUslTools(TestCase):
    def test_random_usl(self):
        u = random_usl()
        self.assertIsInstance(u, Usl)

        u = random_usl(rank_type=Word)
        self.assertIsInstance(u.ieml_object, Word)