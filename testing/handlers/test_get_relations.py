from unittest.case import TestCase

from handlers.dictionary.relations import get_relations
from ieml.ieml_objects.terms import Term
from ieml.script.operator import sc
from models.relations import RelationsConnector


class TestGetRelations(TestCase):
    def test_ordering(self):
        term = Term('wa.')

        result = get_relations({'ieml': str(term.script)})
        self.assertIsInstance(result, list)

        entry = RelationsConnector().get_script(term.script)
        # root is counted as a relation -> +1
        self.assertEqual(len(result), len(entry['RELATIONS']) + 1)

        for rel_e in result:
            self.assertListEqual(sorted(rel_e['rellist'], key=lambda e: sc(e['ieml']), reverse=True), rel_e['rellist'])
