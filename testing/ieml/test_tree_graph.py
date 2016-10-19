import random
from unittest.case import TestCase

from ieml.ieml_objects.commons import TreeGraph


class TestTreeGraph(TestCase):
    def test_transition_order(self):
        r = list(range(1, 10))
        random.shuffle(r)
        transitions = {(0, i, 'data') for i in r}
        tree = TreeGraph(transitions)

        self.assertTupleEqual(list(zip(*tree.transitions[0]))[0], tuple(range(1, 10)))