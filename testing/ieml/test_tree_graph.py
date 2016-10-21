import random
from unittest.case import TestCase
from ieml.ieml_objects.tree_graph import TreeGraph, coord, tree_op, TreePath


class TestTreeGraph(TestCase):
    def _tree_from_range(self, max):
        r = list(range(1, max))
        random.shuffle(r)
        transitions = {(0, i, 'data') for i in r}
        return TreeGraph(transitions)

    def _deep_tree_range(self, max):
        r = [(i, i + 1, 'data') for i in range(max)]
        random.shuffle(r)
        return TreeGraph(r)

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
    def test_path_to_node(self):
        tree = self._tree_from_range(10)

        self.assertEqual(tree[tree.path_of_node(3)][0], 3)

        tree = self._deep_tree_range(10)
        self.assertEqual(tree[tree.path_of_node(10)][0], 10)

        self.assertEqual(tree[tree.path_of_node('data')], ['data' for i in range(10)])


    def test_str(self):
        tree = self._deep_tree_range(10)
        self.assertEqual(str(tree.path_of_node(10)), 's0a0a0a0a0a0a0a0a0a0a0')
        self.assertEqual(str(tree.path_of_node('data')),
                         '(s0m0+s0a0m0+s0a0a0m0+s0a0a0a0m0+s0a0a0a0a0m0+s0a0a0a0a0a0m0+s0a0a0a0a0a0a0m0+'
                         's0a0a0a0a0a0a0a0m0+s0a0a0a0a0a0a0a0a0m0+s0a0a0a0a0a0a0a0a0a0m0)')

