import unittest

from ieml.syntax.sentences import SuperSentence, Sentence
from ieml.syntax.texts import Text
from ieml.usl.sort import square_order_matrix
from ieml.usl.tools import RandomUslGenerator
import numpy as np


class TestUslOrder(unittest.TestCase):
    def setUp(self):
        self.generator = RandomUslGenerator(pool_size=100, level=Text)

    def test_diagonal(self):
        d = square_order_matrix([self.generator(Sentence) for _ in range(30)])
        self.assertTrue(np.count_nonzero(np.diag(d)) == 0)