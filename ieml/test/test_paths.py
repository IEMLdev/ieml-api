from unittest.case import TestCase

from ieml.syntax import Sentence, SuperSentence, Clause, SuperClause, Text, Word, Morpheme
from ieml.dictionary import Term, term
from ieml.tools import RandomPoolIEMLObjectGenerator
from ieml.usl.paths.exceptions import PathError, IEMLObjectResolutionError
from ieml.usl.paths import MultiplicativePath, Coordinate, AdditivePath, ContextPath, path, resolve, enumerate_paths,\
    resolve_ieml_object
from ieml.usl.tools import random_usl, usl


class TestPaths(TestCase):
    def test_path_parser(self):
        p = path("t:sa:sa0:f")
        self.assertIsInstance(p, ContextPath)
        self.assertListEqual([c.__class__ for c in p.children],
                             [Coordinate, MultiplicativePath, MultiplicativePath, Coordinate])
        self.assertEqual(str(p), "t:sa:sa0:f")
        self.assertTupleEqual(tuple(p.context), ({Text}, False, {Text: {Term}}))

        p = path('f15684')
        self.assertIsInstance(p, Coordinate)
        self.assertEqual(p.kind, 'f')
        self.assertEqual(p.index, 15684)
        self.assertTupleEqual(tuple(p.context), ({Word}, False, {Word: {Term}}))

        p = path("t0:(s0a0 + s0m0):s:f + t1:s:s:(r+f)")
        self.assertIsInstance(p, AdditivePath)

        p = path("t:(s+s)a")
        self.assertIsInstance(p, ContextPath)

        with self.assertRaises(PathError):
            p = path("(s:r+s):r")
            print(p)

        p = path("t + s + s:s + r")
        self.assertTupleEqual(p.context, ({Text, SuperSentence, Sentence, Word}, True, {
            Text: {
                SuperSentence, Sentence, Word, Term
            },
            SuperSentence : {
                Sentence,
                Word
            },
            Sentence : {
                Word
            },
            Word : {
                Term
            }
        }))

    def test_context(self):
        with self.assertRaises(PathError):
            p = path("sma")

    def test_resolve(self):
        word = Word(Morpheme([term('wa.')]))
        p = path('r')
        elems = resolve(word, p)
        self.assertSetEqual(elems, {term('wa.')})

        worda = Word(Morpheme([term('wu.')]))
        wordm = Word(Morpheme([term('we.')]))

        s = Sentence([Clause(word, worda, wordm)])
        p = path('sa:r')
        elems = resolve(s, p)
        self.assertSetEqual(elems, {term('wu.')})

        p = path('sa0+s0+sm0')
        elems = resolve(s, p)
        self.assertSetEqual(elems, {word, wordm, worda})


        t = Text([s, word])
        p = path('t')
        elems = resolve(t, p)
        self.assertSetEqual(elems, {s, word})
        p = path('t1')
        elems = resolve(t, p)
        self.assertSetEqual(elems, {s})

    def test_random(self):
        r = RandomPoolIEMLObjectGenerator(level=Sentence)
        s = r.sentence()
        p = path("s+a+m + (s+a+m):(r+f)")
        elems = resolve(s, p)
        self.assertSetEqual(elems, {p for p in s.tree_iter() if isinstance(p, (Word, Term))})

        p = path("t + t:(s+a+m+r+f+(s+a+m):(s+a+m+r+f+(s+a+m):(r+f)))")
        usl = random_usl(rank_type=Text)
        elems = resolve(usl.ieml_object, p)
        self.assertSetEqual(set(e for e in usl.ieml_object.tree_iter() if not isinstance(e, (Text, SuperClause, Clause, Morpheme))), elems)

    def test_enumerate_paths(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        t = r.text()
        e = list(enumerate_paths(t, level=Term))
        self.assertSetEqual({t[1] for t in e}, set(e for e in t.tree_iter() if isinstance(e, Term)))

    def test_rules(self):
        rules0 = [(path('r0'), term('wa.'))]
        obj = resolve_ieml_object(*zip(*rules0))
        self.assertEqual(obj, Word(Morpheme([term('wa.')])))

        rules1 = [(path('r1'), term('wa.')), (path('r'), term('I:')), (path('f0'), term('we.'))]
        obj = resolve_ieml_object(*zip(*rules1))
        word1 = Word(Morpheme([term('I:'), term('wa.')]), Morpheme([term('we.')]))
        self.assertEqual(obj, word1)

        self.assertEqual(resolve_ieml_object(enumerate_paths(obj)), obj)

        r = RandomPoolIEMLObjectGenerator(level=Text)
        t = r.text()
        self.assertEqual(t, resolve_ieml_object(enumerate_paths(t)))

        rules = [(path('r1'), term('wa.')), (path('r'), term('I:')), (path('f0'), term('we.'))]
        obj = resolve_ieml_object(*zip(*rules))
        self.assertEqual(obj, Word(Morpheme([term('I:'), term('wa.')]), Morpheme([term('we.')])))

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
        test([('s:r', term('we.')),('sa0:r', term('wa.'))],
             [('s0m0', "Missing node definition.")])

        # empty rules
        test([],
             [('', "Missing node definition.")])

        # multiple def for a node
        test([('r0', term('wa.')), ('r0', term('we.'))],
             [('r0', 'Multiple definition, multiple ieml object provided for the same node.')])

        # missing index on text
        test([('t:r', term('we.')),('t2:r', term('wa.'))],
             [('', "Index missing on text definition.")])

        # missing index on word
        test([('r2', term('we.')),('r', term('wa.'))],
             [('', "Index missing on word definition.")])

        test([('s:r', term('wa.')), ('sm:r', term('we.')), ('sa1:r', term('wu.'))],
             [('s0a0', 'Missing node definition.')])

        # incompatible path
        test([('t:r', term('wa.')), ('s:f', term('we.'))],
             [('', 'No definition, no type inferred on rules list.')])


        # mulitple errors
        test([("t0:s:f0", term('wa.')), ("t0:sa:r", term('a.')), ('t2:r', term('we.')), ("t0:sm1", Word(Morpheme([term('wu.')])))],
             [('t0:s0', 'No root for the word node.'),
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

        self.assertIsInstance(usl(rules).ieml_object, Word)