import os

from ieml.constants import LANGUAGES, MAX_LAYER
from ieml.dictionary import Dictionary

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


        # for t, r in dic.ranks.items():
        #     self.assertIn(r, list(range(0, 7)), "Term %s as a invalid rank of %d"%(str(t), r))

    # def test_remove(self):
    #     dic = Dictionary()
    #
    #     with self.assertRaises(ValueError):
    #         dic.remove_term(term=term('wa.'))
    #
    #     with self.assertRaises(ValueError):
    #         dic.remove_term(term=term('O:M:.'))
    #
    #     l = len(Dictionary())
    #     for t in ["[O:B:.]", "[O:T:.]", "[U:M:.]", "[A:M:.]", "[O:S:.]"]:
    #         t = term(t)
    #         dic.remove_term(term=t)
    #
    #     self.assertEqual(len(Dictionary()), l-5)
    #
    #     dic.remove_term(term=term('O:M:.'))
    #
    #     with self.assertRaises(TermNotFoundInDictionary):
    #         t = term('O:S:.')
    #
    #     dic.compute_relations()
    #     dic.compute_ranks()
    #
    #     self.assertEqual(len(Dictionary()), l-6)


