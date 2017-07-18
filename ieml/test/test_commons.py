import random
from collections import defaultdict, Counter
from itertools import repeat, chain
from unittest.case import TestCase
from ieml.syntax.sentences import AbstractSentence, SuperSentence, Sentence
from ieml.dictionary import Term, term
from ieml.syntax import Text,Word
from ieml.tools import RandomPoolIEMLObjectGenerator
from ieml.dictionary import script as sc
from ieml.usl.tools import random_usl, replace_paths, usl
from ieml.usl.usl import Usl


class TestTreeStructure(TestCase):
    def test_equal(self):
        t = RandomPoolIEMLObjectGenerator(level=Text).text()
        t2 = Text(children=t.children)
        self.assertNotEqual(id(t), id(t2))
        self.assertEqual(t, t2)

        self.assertEqual(t, str(t))
        self.assertEqual(str(t), t)

    def test_paths(self):
        def test_counter(t):
            c1 = Counter(t for p, t in t.paths.items() for pp in p.develop)

            def elems(node):
                if isinstance(node, Text):
                    return chain.from_iterable(elems(c) for c in node)
                if isinstance(node, AbstractSentence):
                    tree_g = node.tree_graph

                    return chain.from_iterable(elems(k)
                        for k in chain(tree_g.nodes,
                                       [clause.mode for d in tree_g.transitions.values() for a, clause in d]))

                if isinstance(node, Word):
                    return list(k for k in chain(node.root.children,
                                                 [] if node.flexing is not None else node.flexing.children))
                if isinstance(node, Term):
                    return node,

            c2 = Counter(elems(t.ieml_object))
            self.assertEqual(len(c1), len(c2))
            self.assertDictEqual(c1, c2)

            if not isinstance(t, Term):
                self.assertIsNotNone(t.paths)

        for k in (Text, SuperSentence, Sentence, Word, Term):
            t = random_usl(k)
            test_counter(t)

        t = usl("[([([wo.s.-]+[x.t.-]+[t.e.-m.u.-'])*([E:A:.wu.-]+[n.o.-d.o.-'])]*"
            "[([E:A:.wu.-]+[o.wa.-]+[b.e.-s.u.-'])*([M:O:.j.-]+[e.-o.-we.h.-'])]*"
            "[([E:A:.wu.-]+[o.wa.-]+[b.e.-s.u.-'])*([M:O:.j.-]+[e.-o.-we.h.-'])])]")

        test_counter(t)

    def test_replace(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        text = r.text()

        c0 = r.word()
        while text.children[0] == c0:
            c0 = r.word()

        text2 = replace_paths(text, [('t', c0)])
        self.assertTrue(c0 in text2)
        self.assertNotEqual(text2, text)

        t = term('wa.')
        self.assertEqual(replace_paths(t, [('', sc('we.'))]), t)


        t2 = term('we.')
        self.assertEqual(t2, replace_paths(t, [('', t2)]))

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

        text3 = replace_paths(text, args)
        self.assertNotEqual(text, text3)
        self.assertIsInstance(text3, Text)

        # different elements
        args = [(p, r.from_type(p[-1].__class__)) for p, e in args]
        text4 = replace_paths(text, args)
        self.assertNotEqual(text2, text3)


    def _get_child(self):
        pass


class TestUslTools(TestCase):
    def test_random_usl(self):
        u = random_usl()
        self.assertIsInstance(u, Usl)

        u = random_usl(rank_type=Word)
        self.assertIsInstance(u.ieml_object, Word)