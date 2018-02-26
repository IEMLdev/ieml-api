from unittest.case import TestCase

from ieml.exceptions import InvalidPathException
from ieml.dictionary import Term
from ieml.grammar import Text, Word, Theory, Fact, Topic, topic, fact, text
from ieml.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.grammar.paths.exceptions import PathError, IEMLObjectResolutionError
from ieml.grammar.paths import MultiplicativePath, Coordinate, AdditivePath, ContextPath, path, resolve, enumerate_paths,\
    resolve_ieml_object
from ieml.grammar.tools import random_usl, usl


class TestPaths(TestCase):
    def test_path_parser(self):
        p = path("t:sa:sa0:f")
        self.assertIsInstance(p, ContextPath)
        self.assertListEqual([c.__class__ for c in p.children],
                             [Coordinate, MultiplicativePath, MultiplicativePath, Coordinate])
        self.assertEqual(str(p), "t:sa:sa0:f")
        self.assertTupleEqual(tuple(p.context), ({Text}, False, {Text: {Word}}))

        p = path('f15684')
        self.assertIsInstance(p, Coordinate)
        self.assertEqual(p.kind, 'f')
        self.assertEqual(p.index, 15684)
        self.assertTupleEqual(tuple(p.context), ({Topic}, False, {Topic: {Word}}))

        p = path("t0:(s0a0 + s0m0):s:f + t1:s:s:(r+f)")
        self.assertIsInstance(p, AdditivePath)

        p = path("t:(s+s)a")
        self.assertIsInstance(p, ContextPath)

        with self.assertRaises(PathError):
            p = path("(s:r+s):r")
            print(p)

        p = path("t + s + s:s + r")
        self.assertTupleEqual(p.context, ({Text, Theory, Fact, Topic}, True, {
            Text: {
                Theory, Fact, Topic, Word
            },
            Theory : {
                Fact,
                Topic
            },
            Fact : {
                Topic
            },
            Topic : {
                Word
            }
        }))

    def test_context(self):
        with self.assertRaises(PathError):
            p = path("sma")

    def test_resolve(self):
        word = topic([ieml('wa.')])
        p = path('r0')
        elems = resolve(word, p)
        self.assertSetEqual(elems, {ieml('wa.')})

        worda = topic([ieml('wu.')])
        wordm = topic([ieml('we.')])

        s = fact([(word, worda, wordm)])
        p = path('sa:r')
        elems = resolve(s, p)
        self.assertSetEqual(elems, {ieml('wu.')})

        p = path('sa0+s0+sm0')
        elems = resolve(s, p)
        self.assertSetEqual(elems, {word, wordm, worda})


        t = text([s, word])
        p = path('t')
        elems = resolve(t, p)
        self.assertSetEqual(elems, {s, word})
        p = path('t1')
        elems = resolve(t, p)
        self.assertSetEqual(elems, {s})

    def test_random(self):
        r = RandomPoolIEMLObjectGenerator(level=Fact)
        s = r.fact()
        p = path("s+a+m + (s+a+m):(r+f)")
        elems = resolve(s, p)
        self.assertSetEqual(elems, s.topics.union(s.words))

        p = path("t + t:(s+a+m+r+f+(s+a+m):(s+a+m+r+f+(s+a+m):(r+f)))")
        usl = random_usl(rank_type=Text)
        elems = resolve(usl, p)
        self.assertSetEqual(usl.facts.union(usl.topics).union(usl.words).union(usl.theories), elems)

    def test_enumerate_paths(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        t = r.text()
        e = list(enumerate_paths(t, level=Word))
        self.assertSetEqual({t[1] for t in e}, t.words)

    def test_rules(self):
        rules0 = [(path('r0'), ieml('wa.'))]
        obj = resolve_ieml_object(*zip(*rules0))
        self.assertEqual(obj, topic([ieml('wa.')]))

        rules1 = [(path('r1'), ieml('wa.')), (path('r'), ieml('I:')), (path('f0'), ieml('we.'))]
        obj = resolve_ieml_object(*zip(*rules1))
        word1 = topic([ieml('I:'), ieml('wa.')], [ieml('we.')])
        self.assertEqual(obj, word1)

        self.assertEqual(resolve_ieml_object(enumerate_paths(obj)), obj)

        r = RandomPoolIEMLObjectGenerator(level=Text)
        t = r.text()
        self.assertEqual(t, resolve_ieml_object(enumerate_paths(t)))

        rules = [(path('r1'), ieml('wa.')), (path('r'), ieml('I:')), (path('f0'), ieml('we.'))]
        obj = resolve_ieml_object(*zip(*rules))
        self.assertEqual(obj, topic([ieml('I:'), ieml('wa.')], [ieml('we.')]))

    def test_invalid_creation(self):
        def test(rules, expected=None):
            if expected:
                try:
                    usl(rules)
                except IEMLObjectResolutionError as e:
                    self.assertListEqual(e.errors, expected)
                else:
                    self.fail()
            else:
                with self.assertRaises(IEMLObjectResolutionError):
                    usl(rules)

        # missing node definition on sm0
        test([('s:r', ieml('[we.]')),('sa0:r', ieml('[wa.]'))],
             [('s0m0', "Missing node definition.")])

        # empty rules
        test([],
             [('', "Missing node definition.")])

        # multiple def for a node
        test([('r0', ieml('[wa.]')), ('r0', ieml('[we.]'))],
             [('r0', 'Multiple definition, multiple ieml object provided for the same node.')])

        # missing index on text
        test([('t:r', ieml('[we.]')),('t2:r', ieml('[wa.]'))],
             [('', "Index missing on text definition.")])

        # missing index on word
        test([('r2', ieml('[we.]')),('r', ieml('[wa.]'))],
             [('', "Index missing on topic definition.")])

        test([('s:r', ieml('[wa.]')), ('sm:r', ieml('[we.]')), ('sa1:r', ieml('[wu.]'))],
             [('s0a0', 'Missing node definition.')])

        # incompatible path
        test([('t:r', ieml('[wa.]')), ('s:f', ieml('[we.]'))],
             [('', 'No definition, no type inferred on rules list.')])


        # mulitple errors
        test([("t0:s:f0", ieml('[wa.]')), ("t0:sa:r", ieml('[a.]')), ('t2:r', ieml('[we.]')), ("t0:sm1", topic([ieml('[wu.]')]))],
             [('t0:s0', 'No root for the topic node.'),
             ('t0:s0m0', 'Missing node definition.'),
             ('t1', 'Missing node definition.')])

    def test_parse_example(self):
        rules = {
            "r0": "A:O:.wo.t.-",
            "r1": "d.a.-l.a.-f.o.-'",
            "r2": "m.-M:.O:.-'m.-S:.U:.-'E:A:S:.-',",
            "f0": "b.o.-k.o.-s.u.-'",
            "f1": "n.u.-d.u.-d.u.-'"
        }

        self.assertIsInstance(usl(rules), Topic)

    def test_deference(self):
        rand = RandomPoolIEMLObjectGenerator()
        w0 = rand.topic()

        self.assertEqual(w0['r0'], w0.root[0])
        self.assertEqual(w0['r'], w0.root)

        w0 = topic([w0['r0']])

        self.assertEqual(w0['f'], w0.flexing)



