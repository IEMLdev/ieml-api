import os

from ieml.constants import LANGUAGES, MAX_LAYER
from ieml.dictionary_old import Dictionary

from unittest.case import TestCase


class DictionaryTest(TestCase):
    def test_load_dictionary(self):
        dic = Dictionary()
        NB_TERMS = len(dic)

        self.assertEqual(len(dic.index), NB_TERMS)
        self.assertEqual(len(dic.terms), NB_TERMS)
        # self.assertEqual(len(dic.relations), 12)
        for l in LANGUAGES:
            self.assertEqual(len(dic.translations[l]), NB_TERMS)

        self.assertEqual(len(dic.layers), MAX_LAYER + 1) # from 0
        self.assertEqual(sum(len(v) for v in dic.layers), NB_TERMS)
        self.assertListEqual(dic.index, sorted(dic.terms.values()))

    def test_multiple_dictionary(self):
        d0 = Dictionary()
        d1 = Dictionary()
        self.assertEqual(d0, d1)

        d2 = Dictionary('dictionary_2017-06-07_00:00:00')
        self.assertNotEqual(d0, d2)