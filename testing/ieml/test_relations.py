from unittest.case import TestCase

from ieml.script.tools import inverse_relation
from models.relations.relations_queries import RelationsQueries as rq
from models.relations.relations import RelationsConnector as rc

from models.terms.terms import TermsConnector as tc


class TestRelations(TestCase):
    def setUp(self):
        self.inhibitions = {rel['_id']: tc().get_inhibitions(rel['_id']) for rel in rc().relations.find()}
        self.relations = {r: rq.relations(r) for r in self.inhibitions}

    def test_symmetry(self):
        source = 'wa.'
        r = rq.relations(source)

        for reltype in r:
            for s in r[reltype]:
                if source not in rq.relations(s)[inverse_relation(reltype)]:
                    self.fail('Missing link "%s" --> "%s" (%s) in relations db.'%(s, source, reltype))

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