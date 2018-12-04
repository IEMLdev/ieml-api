from itertools import product
from unittest.case import TestCase

from ieml.dictionary_old import Dictionary, term
from ieml.dictionary_old.relations import RELATIONS, INVERSE_RELATIONS


class TestRelations(TestCase):
    def test_symmetry(self):
        t = term('wa.')
        r = t.relations

        for reltype in RELATIONS:
            for tt in r[reltype]:
                if t not in tt.relations[INVERSE_RELATIONS[reltype]]:
                    self.fail('Missing link "%s" --> "%s" (%s) in relations db.'%(str(tt), str(t), reltype))

    def test_no_reflexive_relations(self):
        self.assertEqual(term('O:O:.O:O:.t.-').relations.opposed, ())

    def test_index(self):
        r0 = [t for t in Dictionary()]
        self.assertListEqual(r0, sorted(r0))


    def test_inhibitions(self):
        for t in Dictionary():
            # if Dictionary().inhibitions[t]:
            for reltype in t.inhibitions:
                self.assertTupleEqual(t.relations[reltype], (),
                                     "Term %s has relations %s. Must be inhibited"%(str(t), reltype))

    def test_relations_matrix(self):
        m = Dictionary().relations_graph.connexity
        self.assertTrue(m.any())
        self.assertFalse(m.all())
        self.assertTrue(m.dtype == bool)

    def test_table_relations(self):
        t_p = term("M:M:.u.-")
        t_ss = term("s.u.-")

        # M:M:.O:S:.-
        self.assertTrue(t_p.relations.to(t_ss, relations_types=['table_2']))

    def test_relations_order(self):
        t = term("M:M:.u.-")
        self.assertTupleEqual(t.relations.contains, tuple(sorted(t.relations.contains)))

    def test_relations_to(self):
        self.assertTrue(term('wa.').relations.to(term('we.')))

    def test_neighbours(self):
        for t in Dictionary():
            for k in ['contains', 'contained', 'table_0', 'identity']:
                self.assertIn(k, t.relations.to(t))

            for n in t.relations.neighbours:
                self.assertTrue(t.relations.to(n))

    def test_root_relations(self):
        # if two terms are in the same root paradigms they have to have at least relations between them
        for root in Dictionary().roots:
            for t0, t1 in product(root.relations.contains, root.relations.contains):
                self.assertTrue(t0.relations.to(t1))


