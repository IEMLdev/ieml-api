from unittest.case import TestCase

from handlers.dictionary.commons import relations_order
from handlers.dictionary.relations import get_relations
from ieml.ieml_objects.terms import term
from ieml.script.operator import sc


class TestGetRelations(TestCase):
    def test_ordering(self):
        t = term('wa.')

        result = get_relations({'ieml': str(t.script)})
        self.assertIsInstance(result, list)

        # root is counted as a relation -> +1
        self.assertEqual(len(result), 9)

        for rel_e in result:
            self.assertListEqual(sorted(rel_e['rellist'], key=lambda e: sc(e['ieml']), reverse=True), rel_e['rellist'])

        self.assertListEqual(result, sorted(result, key=lambda rel_entry: relations_order[rel_entry['reltype']]))
