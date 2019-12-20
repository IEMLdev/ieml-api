from itertools import product
from unittest.case import TestCase

from ieml.constants import RELATIONS, INVERSE_RELATIONS
from ieml.dictionary.script import script
from ieml.test.dictionary.dictionary_testcase import DictionaryTestCase


class TestRelations(DictionaryTestCase):
    def test_symmetry(self):
        t = script('wa.')
        r = self.dictionary.relations.relation_object(t)

        for reltype in RELATIONS:
            for tt in r[reltype]:
                if t not in self.dictionary.relations.object(tt, INVERSE_RELATIONS[reltype]):
                    self.fail('Missing link "%s" --> "%s" (%s) in relations db.'%(str(tt), str(t), reltype))

    def test_no_reflexive_relations(self):
        s = script('O:O:.O:O:.t.-')
        self.assertEqual(tuple(self.dictionary.relations.object(s, 'opposed')), ())

    def test_script_sorted(self):
        self.assertListEqual(list(self.dictionary.scripts), sorted(self.dictionary.scripts))

    def test_inhibitions(self):
        for t in self.dictionary.scripts:
            for reltype in self.dictionary._inhibitions[self.dictionary.tables.root(t)]:
                self.assertTupleEqual(tuple(self.dictionary.relations.object(t , reltype)), (),
                                     "Term %s has relations %s. Must be inhibited"%(str(t), reltype))

    def test_table_relations(self):
        t_p = script("M:M:.u.-")
        t_ss = script("s.u.-")

        # M:M:.O:S:.-
        self.assertIn(t_p, self.dictionary.relations.object(t_ss, 'table_2'))

    def test_relations_order(self):
        for s in self.dictionary.scripts:
            relations = self.dictionary.relations.relation_object(s)
            for reltype, values in relations.items():
                self.assertTupleEqual(tuple(values),
                                      tuple(sorted(values)))

    # def test_relations_to(self):
    #     self.assertTrue(script('wa.').relations.to(term('we.')))
    #
    # def test_neighbours(self):
    #     for t in self.d:
    #         for k in ['contains', 'contained', 'table_0', 'identity']:
    #             self.assertIn(k, t.relations.to(t))
    #
    #         for n in t.relations.neighbours:
    #             self.assertTrue(t.relations.to(n))

    def test_root_relations(self):
        # if two terms are in the same root paradigms they have to have at least relations between them
        for root in self.dictionary.tables.roots:
            contains = self.dictionary.relations.relation(root, 'contains')
            for t0, t1 in product(contains, contains):
                self.assertTrue(self.dictionary.relations.relation(t0, t1))


