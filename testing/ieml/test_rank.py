import unittest
# We use protected method _compute_rank for dependency injection
from ieml.ieml_objects.dictionary import Dictionary
from ieml.script.tables import get_table_rank, _compute_rank, generate_tables
from ieml.script.operator import sc
from ieml.script.tools import factorize


class RankComputationTest(unittest.TestCase):

    # TODO: Tests for paradigms built from 3d tables

    def setUp(self):
        self.dic = Dictionary()

    def test_rank1_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]
        self.assertTrue(term.rank == 1, "The rank of a root paradigm is 1")

    def test_rank2_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]

        root_table = term.tables[1]
        h = root_table.headers[next(root_table.headers.__iter__())]
        term = self.dic.terms[sc([h.columns[4],h.columns[5],h.columns[3]])]

        self.assertEqual(term.rank, 2)

    def test_rank3_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]

        root_table = term.tables[1]
        h = root_table.headers[next(root_table.headers.__iter__())].rows[2]
        term = self.dic.terms[h]

        self.assertEqual(term.rank, 3)

        self.assertEqual(term("[T:M:.e.-M:M:.i.-wa.e.-']"), 3)

    def test_rank4_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        root_table = term.tables[1]
        h = root_table.headers[next(root_table.headers.__iter__())].rows[2]
        term = self.dic.terms[h]

        root_table = term.tables[0]
        h = root_table.headers[next(root_table.headers.__iter__())].columns
        print(str(term))

        term = self.dic.terms[sc([h[0], h[1]])]
        print(str(term))

        self.assertEqual(term.rank, 4)

    def test_rank5_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        root_table = term.tables[1]
        h = root_table.headers[next(root_table.headers.__iter__())].rows[2]
        term = self.dic.terms[h]

        root_table = term.tables[0]
        h = root_table.headers[next(root_table.headers.__iter__())].rows[0]
        term = self.dic.terms[h]

        self.assertEqual(term.rank, 5)

    def test_paradigm_from_multiple_tables(self):
        term = self.dic.terms[sc("S:M:.e.-M:M:.u.-wa.e.-'+B:M:.e.-M:M:.a.-wa.e.-'+T:M:.e.-M:M:.i.-wa.e.-'")]
        self.assertEquals(term.rank, 2)

    def test_additive_parent_paradigm(self):
        term = self.dic.terms[sc("O:M:.M:M:.-")]
        self.assertEquals(term.rank, 1)


if __name__ == '__main__':
    unittest.main()
