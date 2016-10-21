from collections import namedtuple
from typing import NamedTuple

import itertools

from ieml.exceptions import InvalidPathException

TREE_ROLES = {'m', 'a', 's'}

coord = namedtuple('Coord', ['role', 'branch'])
tree_op = namedtuple('TreeOp', ['type', 'args'])


class TreePath:
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
                if isinstance(e, coord):
                    return [e]
                if isinstance(e, tree_op):
                    if e.type == '+':
                        res = []
                        for a in [_develop(k) for k in e.args]:
                            res += a

                        return res
                    else:
                        return list(itertools.product(*(_develop(k) for k in e.args)))

            self._development = tree_op(type='+', args=[tree_op(type='*', args=product)
                                                        for product in _develop(self.coordinate)])

        return self._development


class TreeStructure:
    def __init__(self):
        super().__init__()
        self._str = None
        self._paths = None
        self.children = None  # will be an iterable (list or tuple)

    def __str__(self):
        return self._str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """Two propositions are equal if their children'list or tuple are equal"""
        if not isinstance(other, (TreeStructure, str)):
            return False

        return self._str == str(other)

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __iter__(self):
        """Enables the syntactic sugar of iterating directly on an element without accessing "children" """
        return self.children.__iter__()

    def tree_iter(self):
        yield self
        for c in self.children:
            yield from c.tree_iter()

    def path(self, path):
        if len(path) == 0:
            return [self]

        p = path[0]
        for e in self._resolve_coordinates(p):
            return sum(e.path(path[1:]))

        raise InvalidPathException(self, path)

    def _resolve_coordinates(self, path):
        raise NotImplemented

    @property
    def paths(self):
        if not self._paths:
            self._paths = [[child] + path for child in self.children for path in child.paths] \
                if self.children else [[]]

        return self._paths


LAYER_MARKS = [
    ':',
    '.',
    '-',
    '\'',
    ',',
    '_',
    ';'
]