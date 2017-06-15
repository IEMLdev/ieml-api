from collections import defaultdict
from typing import Callable

import numpy as np

from ieml.ieml_objects.terms.tools import term
from ieml.script.tools import factorize


class Table:
    def __init__(self, cells, factorize_fn):
        super().__init__()

        if not isinstance(cells, np.ndarray) or cells.ndim != 2:
            raise ValueError("Must provide a 2d numpy array to create a Table object")

        if not isinstance(factorize_fn, Callable):
            raise ValueError("Must provide a function to factorize the cells into the headers")

        self.cells = cells
        self.factorize_fn = factorize_fn

        self.dim = 2 if all(s != 1 for s in self.cells.shape) else 1

        self.rows = None
        self.columns = None
        self.head = None
        self._build_headers()

    def _build_headers(self):
        if self.dim == 1:
            self.rows = []
            self.columns = []
            self.head = self.factorize_fn(list(self))
        else:
            self.rows = [self.factorize_fn(list(self.cells[i,:])) for i in range(self.shape[0])]
            self.columns = [self.factorize_fn(list(self.cells[:, j])) for j in range(self.shape[1])]
            self.head = self.factorize_fn(self.rows)

    @property
    def shape(self):
        return self.cells.shape

    def index(self, item):
        if item not in self:
            return []

        if self._index is None:
            self._index = {c: tuple(*zip(*np.where(self.cells == c))) for c in self}

        return [self._index[c] for c in item]

    def project(self, elements, key):
        result = defaultdict(list)

        for cell in self:
            result[cell] = [e for e in elements if key(cell, e)]

        return result

    def __eq__(self, other):
        return isinstance(other, Table) and self.head == other.head

    def __hash__(self):
        return self.head.__hash__()

    def __contains__(self, item):
        return item in self.head

    def __iter__(self):
        return np.nditer(self.cells, flags=['refs_ok'])


def get_tables_for_term(t):
    return [Table(cells[:,:,i], factorize_fn=factorize) for cells in term(t).script.cells
            for i in range(cells.shape[2])]

if __name__ == '__main__':
    t = get_tables_for_term('M:O:.M:M:.-')
    print([str(c) for c in t[0]])