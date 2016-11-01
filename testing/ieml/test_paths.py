from unittest.case import TestCase

from ieml.ieml_objects.sentences import Sentence, SuperSentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word
from ieml.paths.exceptions import PathError
from ieml.paths.paths import Path, MultiplicativePath, Coordinate, AdditivePath, ContextPath
from ieml.paths.tools import path


class TestPaths(TestCase):
    def test_path_parser(self):
        p = path("t:sa:sa0:f")
        self.assertIsInstance(p, ContextPath)
        self.assertListEqual([c.__class__ for c in p.children],
                             [Coordinate, MultiplicativePath, MultiplicativePath, Coordinate])
        self.assertEqual(str(p), "t:sa:sa0:f")
        self.assertTupleEqual(p.context, ({Text}, False, {Text: {Term}}))

        p = path('f15684')
        self.assertIsInstance(p, Coordinate)
        self.assertEqual(p.kind, 'f')
        self.assertEqual(p.index, 15684)
        self.assertTupleEqual(p.context, ({Word}, False, {Word: {Term}}))

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
