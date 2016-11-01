from itertools import groupby

from ieml.paths.constants import COORDINATES_KINDS, KIND_TO_RANK


class Path:
    def __init__(self, children, rank):
        self.children = tuple(children)
        self.rank = rank


class AdditivePath(Path):
    def __init__(self, children):
        if not children:
            raise ValueError('Must be a non empty children in a Additive Path.')

        try:
            children = list(children)
        except TypeError:
            raise ValueError("The children must be iterable.")

        if any(not isinstance(child, Path) for child in children):
            raise ValueError('The children must be path instances.')

        # addition unfold
        _children = []
        for c in children:
            if isinstance(c, AdditivePath):
                _children += c.children
            else:
                if len(c.children) == 1:
                    _children.append(c.children[0])
                else:
                    _children.append(c)

        _rank = _children[0].rank
        if any(c.rank != _rank for c in _children):
            raise ValueError('The operand of the addtion must have the same rank.')

        super().__init__(_children, _rank)

    def __str__(self):
        return '+'.join(map(str, self.children))


class MultiplicativePath(Path):
    def __init__(self, children):
        if not children:
            raise ValueError('Must be a non empty children in multiplicative path.')

        try:
            children = list(children)
        except TypeError:
            raise ValueError('The children of a multiplicative path must be iterable.')

        if any(not isinstance(c, Path) for c in children):
            raise ValueError('The children must be of type Path.')

        # multiplication unfold
        _children = []
        for c in children:
            if isinstance(c, MultiplicativePath):
                _children += list(c.children)
            else:
                if len(c.children) == 1:
                    # single element addition, can be simplified
                    _children += [c.children[0]]
                else:
                    # coord or multi add
                    _children += [c]

        # rank check
        rank = _children[0].rank
        _rank = rank
        for c in _children:
            if c.rank not in (_rank, _rank - 1):
                raise ValueError("Invalid rank ordering in multiplicative path.")
            _rank = c.rank

        self.ranks = {r: v for r, v in groupby(_children, lambda c: c.rank)}

        super().__init__(_children, _rank)

    def __str__(self):
        _stages = []
        for _stage in sorted(self.ranks):
            res = ''
            for child in self.ranks[_stage]:
                if isinstance(child, AdditivePath):
                    res += '(%s)'%str(child)
                else:
                    res += str(child)
            _stages.append(res)

        return ':'.join(_stages)


class Coordinate(Path):
    def __init__(self, kind, rank, index=None):

        if not isinstance(kind, str) or not len(kind) == 1 or not kind in COORDINATES_KINDS:
            raise ValueError("A coordinate kind must be one of the following (%s)."%
                             ', '.join(map(str, COORDINATES_KINDS)))

        self.kind = kind

        if not isinstance(rank, int):
            raise ValueError('The rank must be an integer.')

        if kind in KIND_TO_RANK and rank != KIND_TO_RANK[kind]:
            raise ValueError("Invalid rank for this kind.")

        self.rank = rank

        if index:
            if not isinstance(index, int):
                raise ValueError("Coordinate index must be int.")

            self.index = index
        else:
            self.index = None

        super().__init__((), rank)

    def __str__(self):
        return self.kind + (str(self.index) if self.index else '')

