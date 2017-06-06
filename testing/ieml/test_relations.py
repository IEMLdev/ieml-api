from unittest.case import TestCase

from ieml.ieml_objects.dictionary import Dictionary
from ieml.ieml_objects.relations import RELATIONS
from ieml.ieml_objects.tools import term
from ieml.script.tools import inverse_relation


class TestRelations(TestCase):
    def test_symmetry(self):
        t = term('wa.')
        r = t.relations

        for reltype in RELATIONS:
            for tt in r[reltype]:
                if t not in tt.relations[inverse_relation(reltype)]:
                    self.fail('Missing link "%s" --> "%s" (%s) in relations db.'%(str(tt), str(t), reltype))

    def test_no_reflexive_relations(self):
        self.assertEqual(term('O:O:.O:O:.-').relations.opposed, ())

    def test_index(self):
        r0 = [t for t in Dictionary()]
        self.assertListEqual(r0, sorted(r0))

    def test_relations_graph(self):
        m = Dictionary().relations_graph(['etymology', 'inclusion'])
        s = len(Dictionary())
        self.assertEqual(m.shape, (s, s))


    def test_inhibitions(self):
        for t in Dictionary():
            # if Dictionary().inhibitions[t]:
            for reltype in t.inhibitions:
                self.assertTupleEqual(t.relations[reltype], (),
                                     "Term %s has relations %s. Must be inhibited"%(str(t), reltype))

    def test_relations_matrix(self):
        for reltype in RELATIONS:
            if reltype in ('father', 'child', 'etymology', 'siblings', 'table'):
                continue
            self.assertEqual(Dictionary().rel(reltype).min(), 0)
            self.assertEqual(Dictionary().rel(reltype).max(), 1,
                             "%s -> max %d"%(reltype, Dictionary().rel(reltype).max()))

    def test_table_relations(self):
        t_p = term("M:M:.u.-")
        t_ss = term("s.u.-")

        self.assertFalse(t_p.relations.to(t_ss, relations_types=['table_2']))
