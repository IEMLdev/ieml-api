import unittest

from ieml.distance.sort import square_order_matrix
from ieml.lexicon import Fact, Text
import numpy as np

from ieml.lexicon.tools import RandomUslGenerator


class TestUslOrder(unittest.TestCase):
    def setUp(self):
        self.generator = RandomUslGenerator(pool_size=100, level=Text)

    def test_diagonal(self):
        d = square_order_matrix([self.generator(Fact) for _ in range(30)])
        self.assertFalse((np.diag(d) == 0).any())