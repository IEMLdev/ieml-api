import unittest

from ieml.grammar.morpheme import morpheme


class MorphemeTestCase(unittest.TestCase):
    def test_empty(self):
        m = morpheme([])