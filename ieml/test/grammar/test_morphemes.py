import unittest

from ieml.lexicon.morpheme import morpheme


class MorphemeTestCase(unittest.TestCase):
    def test_empty(self):
        m = morpheme([])