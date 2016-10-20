import random
from unittest.case import TestCase

from ieml.commons import TreePath, tree_op, coord
from ieml.ieml_objects.commons import TreeGraph


class TestTreeGraph(TestCase):
    def _tree_from_range(self, max):
        r = list(range(1, 10))
        random.shuffle(r)
        transitions = {(0, i, 'data') for i in r}
        return TreeGraph(transitions)

    def test_transition_order(self):
        tree = self._tree_from_range(10)
        self.assertTupleEqual(list(zip(*tree.transitions[0]))[0], tuple(range(1, 10)))

    def test_path_from_node(self):
        tree = self._tree_from_range(10)
        path = tree.path_of_node(3)
        self.assertEqual(path, TreePath(tree_op(type='*', args=(
                                                    coord(role='s', branch=0),
                                                    coord(role='a', branch=2)))))
        path = tree.path_of_node('data')

        self.assertEqual(path, TreePath(tree_op(type='*', args=(
                                                    coord(role='s', branch=0),
                                                    tree_op(type='+', args=tuple(
                                                        coord(role='m', branch=i) for i in range(0, 9)
                                                    ))))))

