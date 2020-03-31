from unittest import TestCase

from ieml.dictionary.dictionary import Dictionary
from ieml.dictionary.table.table import Table
from ieml.ieml_database import IEMLDatabase, GitInterface


class TestTables(TestCase):
    def setUp(self):
        self.db = IEMLDatabase(folder=GitInterface().folder)
        self.d = self.db.get_dictionary()

    def test_iterable(self):
        try:
            all(self.assertIsInstance(t, Table) for t in self.d.tables)
        except TypeError:
            self.fail()
    #
    def test_shape(self):
        for s in self.d.scripts:
            self.assertIsInstance(s.cells, tuple)
            for c in s.cells:
                self.assertEqual(c.ndim, 3)

        # for t in self.d.tables:
        #     self.assertEqual(t.shape, )