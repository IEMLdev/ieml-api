from unittest.case import TestCase

from ieml.ieml_objects.dictionary import Dictionary, RELATION_TYPES_TO_INDEX
from ieml.ieml_objects.tools import term
from ieml.script.tools import inverse_relation


class TestRelations(TestCase):
    def test_symmetry(self):
        t = term('wa.')
        r = t.relations

        for reltype in RELATION_TYPES_TO_INDEX:
            for s in r[RELATION_TYPES_TO_INDEX[reltype]]:
                if t not in s.relations[RELATION_TYPES_TO_INDEX[inverse_relation(reltype)]]:
                    self.fail('Missing link "%s" --> "%s" (%s) in relations db.'%(s, t, reltype))

    def test_no_reflexive_relations(self):
        self.assertEqual(term('O:O:.O:O:.-').relations.opposed, [])

    def test_index(self):
        r0 = [t for t in Dictionary()]
        self.assertListEqual(r0, sorted(r0))

    def test_inhibition(self):
        for term, rels in self.relations.items():
            for reltype in rels:
                if reltype == 'ROOT':
                    continue

                relkey = '.'.join(reltype.split('.')[:2])
                if relkey in self.inhibitions[term] and len(rels[reltype]) != 0:
                    self.fail('Link "%s" --> "%s" (%s), but it must be inhibited.'%(term, rels[reltype][0], relkey))

                for s in rels[reltype]:
                    relkey = '.'.join(inverse_relation(reltype).split('.')[:2])

                    if relkey in self.inhibitions[s]:
                        self.fail('Link "%s" --> "%s" (%s) but the inverse relation (%s) is inhibited in "%s"' %
                                  (term, s, reltype, relkey, s))

    def test_inhibit(self):
        rq._do_inhibition(rq._inhibitions())