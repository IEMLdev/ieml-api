import random
from unittest.case import TestCase
from ieml.lexicon.tree_graph import TreeGraph


class TestTreeGraph(TestCase):
    def _tree_from_range(self, max):
        r = list(range(1, max))
        random.shuffle(r)
        transitions = {(0, i, 'data') for i in r}
        return TreeGraph(transitions)

    def test_transition_order(self):
        tree = self._tree_from_range(10)
        self.assertTupleEqual(list(zip(*tree.transitions[0]))[0], tuple(range(1, 10)))
