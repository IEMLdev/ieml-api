import itertools
from collections import defaultdict, namedtuple
from itertools import chain

import numpy

from ieml.exceptions import InvalidPathException
from ieml.ieml_objects.exceptions import InvalidTreeStructure
from ieml.ieml_objects.paths import IEMLCoordinate


class TreeGraph:
    def __init__(self, list_transitions):
        """
        Transitions list must be the (start, end, data) the data will be stored as the transition tag
        :param list_transitions:
        """
        # transitions : dict
        #
        self.transitions = defaultdict(list)
        for t in list_transitions:
            self.transitions[t[0]].append((t[1], t))

        self.nodes = sorted(set(self.transitions) | {e[0] for l in self.transitions.values() for e in l})

        # sort the transitions
        for s in self.transitions:
            self.transitions[s].sort(key=lambda t: self.nodes.index(t[0]))

        self.nodes_index = {n: i for i, n in enumerate(self.nodes)}
        _count = len(self.nodes)
        self.array = numpy.zeros((len(self.nodes), len(self.nodes)), dtype=bool)

        for t in self.transitions:
            for end in self.transitions[t]:
                self.array[self.nodes_index[t]][self.nodes_index[end[0]]] = True

        # checking
        # root checking, no_parent hold True for each index where the node has no parent
        parents_count = numpy.dot(self.array.transpose().astype(dtype=int), numpy.ones((_count,), dtype=int))
        no_parents = parents_count == 0
        roots_count = numpy.count_nonzero(no_parents)

        if roots_count == 0:
            raise InvalidTreeStructure('No root node found, the graph has at least a cycle.')
        elif roots_count > 1:
            raise InvalidTreeStructure('Several root nodes found.')

        self.root = self.nodes[no_parents.nonzero()[0][0]]

        if (parents_count > 1).any():
            raise InvalidTreeStructure('A node has several parents.')

        def __stage():
            current = [self.root]
            while current:
                yield current
                current = [child[0] for parent in current for child in self.transitions[parent]]

        self.stages = list(__stage())

    def __getitem__(self, item):
        if not isinstance(item, TreePath):
            raise ValueError('Invalid argument %s, must specify a TreePath object to access node '
                             'in a TreeGraph.'%str(item))
        result = []

        for product in item.develop().args:
            current = self.root
            if len(product.args) == 1:
                result.append(current)
                break

            end = False
            for c in product.args[1:]:
                if end:
                    raise InvalidPathException(self, item)

                try:
                    current = self.transitions[current][c.branch][1]
                except KeyError:
                    raise InvalidPathException(self, item)

                if c.role == 'm':
                    end = True
                    current = current[2]
                elif c.role == 'a':
                    current = current[1]
                else:
                    raise InvalidPathException(self, item)

            result.append(current)

        return result

    def path_of_node(self, node):
        if node in self.nodes:
            nodes = [(node, False)]
        else:
            nodes = []

        # can be a mode
        nodes += [(c[0], True) for c_list in self.transitions.values() for c in c_list if c[1][2] == node]
        if not nodes:
            raise ValueError("Node not in tree graph : %s" % str(node))

        def _build_coord(node, mode=False):
            if node == self.root:
                return [coord(branch=0, role='s')]

            parent = self.nodes[numpy.where(self.array[:, self.nodes_index[node]])[0][0]]
            return _build_coord(parent) + [coord(branch=[c[0] for c in self.transitions[parent]].index(node),
                                                 role='m' if mode else 'a')]

        return TreePath(tree_op(type='+', args=[
            tree_op(type='*', args=_build_coord(node, mode)) for node, mode in nodes
        ]))


TREE_ROLES = {'m', 'a', 's'}
coord = namedtuple('Coord', ['role', 'branch'])
tree_op = namedtuple('TreeOp', ['type', 'args'])


class TreePath(IEMLCoordinate):
    def __init__(self, arg):
        self.coordinate = None

        if isinstance(arg, (tree_op, coord)):
            self.coordinate = arg
        else:
            raise ValueError("A tree coordinate can't be instancied with %s"%str(arg))

        # check and make immutable
        def check(tree):
            if isinstance(tree, coord):
                if tree.role not in TREE_ROLES:
                    raise ValueError("Invalid role for a coordinate %s, must be s, a or m."%str(tree.role))

                if not isinstance(tree.branch, int):
                    raise ValueError("Invalid branch number for a coordinate %s, must be int."%str(tree.branch))

                return tree

            if isinstance(tree, tree_op):
                if tree.type not in ('+', '*'):
                    raise ValueError("Invalid type for a tree operator %s, must be + or *."%str(tree.type))

                try:
                    arguments = tuple(check(arg) for arg in tree.args)
                except TypeError:
                    raise ValueError(
                        "Invalid argument for a tree operator %s, must be an iterable."%str(tree.args))

                if len(arguments) == 0:
                    raise ValueError("Invalid argument length for a tree operator %s, must be an iterable."
                                     % str(tree.args))

                if len(arguments) == 1:
                    return arguments[0]

                return tree_op(args=arguments, type=tree.type)

            raise ValueError("%s is not a coordinate nor a tree operator object."%str(tree))

        self.coordinate = check(self.coordinate)

        super().__init__()

        self._development = None

    def __eq__(self, other):
        if isinstance(other, TreePath):
            return self.develop() == other.develop()

        raise NotImplemented

    def __hash__(self):
        return hash(self.develop())

    def __str__(self):
        def _render_coord(coords, first=True):
            if isinstance(coords, tree_op):
                if coords.type == '*':
                    result = ''
                    for i, a in enumerate(coords.args):
                        result += _render_coord(a, first=True) #+ LAYER_MARKS[min(i, len(LAYER_MARKS) - 1)]
                    return result
                else:
                    result = coords.type.join(_render_coord(a) for a in coords.args)
                    if first:
                        result = '(' + result + ')'
                    return result
            else:
                # coord type
                return coords.role + str(coords.branch)

        return _render_coord(self.coordinate)

    def develop(self):

        if not self._development:
            def _develop(e):
                """

                :param e:
                :return: a list of list : a list of product
                """
                if isinstance(e, coord):
                    return [(e,)]
                if isinstance(e, tree_op):
                    if e.type == '+':
                        res = []
                        for a in [_develop(k) for k in e.args]:
                            res += a

                        return res
                    else:
                        return [tuple(chain.from_iterable(r))
                                for r in itertools.product(*(_develop(k) for k in e.args))]

            self._development = tree_op(type='+', args=tuple(tree_op(type='*', args=product)
                                                        for product in _develop(self.coordinate)))

        return self._development

    def _do_add(self, other):
        return TreePath(tree_op(type='+', args=[self.coordinate, other.coordinate]))