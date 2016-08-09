from ieml.script.constants import OPPOSED_SIBLING_RELATION
from models.relations.relations_queries import RelationsQueries
from testing.models.stub_db import ModelTestCase
from testing.models.test_model import paradigms


class TestRelationCollection(ModelTestCase):
    def setUp(self):
        super().setUp()
        self._clear()
        for p in paradigms:
            self._save_paradigm(paradigms[p], recompute_relations=False)

        self.terms.recompute_relations()

    def test_no_reflexive_relations(self):
        self.assertEqual(RelationsQueries.relations('O:O:.O:O:.-', OPPOSED_SIBLING_RELATION), [])