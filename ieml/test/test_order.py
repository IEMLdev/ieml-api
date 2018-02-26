import unittest

from ieml.grammar import Fact, Text
import numpy as np

from ieml.grammar.tools import RandomUslGenerator


class TestUslOrder(unittest.TestCase):
    def setUp(self):
        self.generator = RandomUslGenerator(pool_size=100, level=Text)

    def test_diagonal(self):
        d = square_order_matrix([self.generator(Fact) for _ in range(30)])
        self.assertTrue(np.count_nonzero(np.diag(d)) == 0)