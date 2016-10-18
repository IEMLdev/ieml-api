import random
from collections import defaultdict, Counter
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

    def test_paths(self):
        t = RandomPoolIEMLObjectGenerator(level=Text).text()

        self.assertDictEqual(Counter((p[-1] for p in t.paths)),
                             Counter((p for p in t.tree_iter() if isinstance(p, Term))))
        self.assertIsNotNone(t._paths)

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

        paths = random.sample(text.paths, random.randint(2, len(text.paths)))
        args = []
        for p in paths:
            i = random.randint(0,1)
            if i:
                args.append((p, r.term()))
            else:
                p = p[:-random.randint(1, len(p) - 2)]
                if not p[-1].closable:
                    p = p[:-1]
                self.assertTrue(p[-1].closable)
                args.append((p, r.from_type(p[-1].__class__)))

        text3 = replace_from_paths(text, *zip(*args))
        self.assertNotEqual(text, text3)
        self.assertIsInstance(text3, Text)

        # different elements
        args = [(p, r.from_type(p[-1].__class__)) for p, e in args]
        text4 = replace_from_paths(text, *zip(*args))
        self.assertNotEqual(text2, text3)


    def _get_child(self):
        pass


class TestUslTools(TestCase):
    def test_random_usl(self):
        u = random_usl()
        self.assertIsInstance(u, Usl)

        u = random_usl(rank_type=Word)
        self.assertIsInstance(u.ieml_object, Word)