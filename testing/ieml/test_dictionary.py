import os

from ieml.commons import LANGUAGES
from ieml.ieml_objects.dictionary import Dictionary
from unittest.case import TestCase

from ieml.script.constants import MAX_LAYER


class DictionaryTest(TestCase):
    def test_load_dictionary(self):
        dic = Dictionary()
        NB_TERMS = 4235
        NB_ROOTS = 54

        self.assertEqual(len(dic), NB_TERMS)
        self.assertEqual(len(dic.terms), NB_TERMS)
        self.assertEqual(len(dic.ranks), NB_TERMS)
        # self.assertEqual(len(dic.relations), 12)
        for l in LANGUAGES:
            self.assertEqual(len(dic.translations[l]), NB_TERMS)

        self.assertEqual(len(dic.roots), NB_ROOTS)

        self.assertEqual(len(dic.layers), MAX_LAYER + 1) # from 0
        self.assertEqual(sum(len(v) for v in dic.layers), NB_TERMS)
        self.assertListEqual(dic.index, sorted(dic.terms.values()))

        self.assertEqual(len(dic.singular_sequences), sum(r.script.cardinal for r in dic.roots))

        for t, r in dic.ranks.items():
            self.assertIn(r, list(range(1, 7)), "Term %s as a invalid rank of %d"%(str(t), r))


