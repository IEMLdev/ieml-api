import unittest
# We use protected method _compute_rank for dependency injection
from ieml.dictionary import Dictionary
from ieml.dictionary.script import script as sc, AdditiveScript
from ieml.ieml_database import IEMLDatabase, GitInterface


class RankComputationTest(unittest.TestCase):

    # TODO: Tests for paradigms built from 3d tables
    @classmethod
    def setUpClass(cls) -> None:
        cls.dic = IEMLDatabase(folder=GitInterface().folder).get_dictionary()

    def test_rank1_2d(self):
        for t in self.dic.tables.roots:
            self.assertTrue(self.dic.tables[t].rank == 0, "The rank of a root paradigm is not 0")

    def test_rank2_2d(self):
        term = sc("O:M:.M:M:.-+M:M:.O:M:.-")

        root_table = self.dic.tables.root(term)
        h = self.dic.tables[root_table]
        first_t = self.dic.tables[h.tables[1]]
        term = sc(AdditiveScript([first_t.columns[4],first_t.columns[5],first_t.columns[3]]), factorize=True)

        self.assertEqual(self.dic.tables[term].rank, 2)

    def test_rank3_2d(self):
        t = self.dic.tables[sc("c.-'O:M:.-'n.o.-s.o.-',")]

        self.assertEqual(t.rank, 3)

    def test_rank4_2d(self):
        t = self.dic.tables["E:.-U:.S:M:.-l.-'"]

        self.assertEqual(t.rank, 5)

    def test_rank5_2d(self):
        term = self.dic.tables[sc("O:M:.M:M:.-+M:M:.O:M:.-")]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        root_table = self.dic.tables[term.tables[1]]
        root_table = root_table.rows[2]
        h = self.dic.tables[root_table].rows[0]

        self.assertEqual(self.dic.tables[h].rank, 5)

    def test_paradigm_from_multiple_tables(self):
        term = self.dic.tables[sc("S:M:.e.-M:M:.u.-wa.e.-'+B:M:.e.-M:M:.a.-wa.e.-'+T:M:.e.-M:M:.i.-wa.e.-'")]
        self.assertEqual(term.rank, 1)

    def test_additive_parent_paradigm(self):
        term = self.dic.tables[sc("O:M:.M:M:.-")]
        self.assertEqual(term.rank, 1)

    def test_rank0(self):
        self.assertListEqual([t for t in self.dic.scripts if self.dic.tables[t].rank == 0], sorted(self.dic.tables.roots))

if __name__ == '__main__':
    unittest.main()
