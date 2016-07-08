import unittest
# We use protected method _compute_rank for dependency injection
from ieml.script.tables import get_table_rank, _compute_rank, generate_tables
from ieml.operator import sc
from ieml.script.tools import factorize


class RankComputationTest(unittest.TestCase):

    def test_rank1_2d(self):
        root_paradigm = sc("O:M:.M:M:.-+M:M:.O:M:.-")
        self.assertTrue(get_table_rank(root_paradigm) == 1, "The rank of a root paradigm is 1")

    def test_rank2_2d(self):
        root_paradigm = sc("O:M:.M:M:.-+M:M:.O:M:.-")
        root_table = generate_tables(root_paradigm)[1]
        paradigm = factorize([root_table.headers[1][2], root_table.headers[1][5]])
        self.assertEqual(_compute_rank(paradigm, root_paradigm), 2)

    def test_rank3_2d(self):
        root_paradigm = sc("O:M:.M:M:.-+M:M:.O:M:.-")
        root_table = generate_tables(root_paradigm)[1]
        paradigm = root_table.headers[1][2]
        self.assertEqual(_compute_rank(paradigm, root_paradigm), 3)

    def test_rank4_2d(self):
        root_paradigm = sc("O:M:.M:M:.-+M:M:.O:M:.-")
        root_table = generate_tables(root_paradigm)[1]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        rank_3_table = generate_tables(root_table.headers[1][2])[0]
        paradigm = factorize([rank_3_table.headers[0][0], rank_3_table.headers[0][1]])
        self.assertEqual(_compute_rank(paradigm, root_paradigm), 4)

    def test_rank5_2d(self):
        root_paradigm = sc("O:M:.M:M:.-+M:M:.O:M:.-")
        root_table = generate_tables(root_paradigm)[1]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        rank_3_table = generate_tables(root_table.headers[1][2])[0]
        paradigm = rank_3_table.headers[0][0]
        self.assertEqual(_compute_rank(paradigm, root_paradigm), 5)


if __name__ == '__main__':
    unittest.main()
