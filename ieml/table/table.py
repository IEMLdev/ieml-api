from collections import namedtuple
import numpy as np


Cell = namedtuple('Cell', ['row', 'column', 'coordinate', 'table', 'element'])


class Table:
    def __init__(self, paradigm):
        super().__init__()
        self._index = None

        self.paradigm = paradigm
        self.type = paradigm.__class__

        self.cells_array = paradigm.cells()

        if not isinstance(self.cells_array, np.ndarray) or self.cells_array.ndim != 2:
            raise ValueError("Must provide a 2d numpy array to create a Table object")

        self.rows, self.columns = paradigm.headers()
        self.dim = 2 if all(s != 1 for s in self.shape) else 1

        def _cell(e):
            i, j = self.index(e)
            return Cell(row=self.rows[i], column=self.columns[j], coordinate=(i, j), table=self, element=e)

        self.cells = {
            e: _cell(e) for e in self
        }

    @property
    def shape(self):
        return self.cells_array.shape

    def index(self, item):
        if self._index is None:
            self._index = {c: tuple(*zip(*np.where(self.cells_array == c))) for c in self}

        if isinstance(item, self.type):
            if item not in self:
                return None
            return self._index[item]
        else:
            return [self.index(c) for c in item]

    def project(self, elements, key):
        result = {}
        for e in elements:
            result[e] = [c for c in self if key(c.element, e)]

        return result

    def __eq__(self, other):
        return isinstance(other, Table) and self.paradigm == other.paradigm

    def __hash__(self):
        return self.paradigm.__hash__()

    def __contains__(self, item):
        return item in self.paradigm

    def __iter__(self):
        return map(lambda e: e[()],
                   np.nditer(self.cells_array, flags=['refs_ok'], op_flags=['readonly']))

    def __str__(self):
        return "<Table %s %s, (%d, %d)>"%(self.type.__name__, str(self.paradigm), *self.shape)

if __name__ == '__main__':
    from ieml.ieml_objects.terms import term
    t = Table(term('M:O:.M:M:.-'))
    print(t)