import collections
from collections import defaultdict
from itertools import chain

import numpy as np

from ieml.ieml_objects.terms import Term, term, TermNotFoundInDictionary
from ieml.script.operator import script
from ieml.script.script import Script

Cell = collections.namedtuple('Cell', ['row', 'column', 'coordinate', 'table', 'script', 'term'])

_terms = defaultdict(list)


class Table:
    def __init__(self, paradigm):
        super().__init__()

        self.paradigm = term(paradigm)
        if self.paradigm.script.cardinal == 1:
            raise ValueError("Table are defined on paradigm, not singular sequences.")

        self._index = {}

        cells = self.paradigm.cells()
        self.dim = 2 if all(s != 1 for s in cells.shape) else 1

        def _cell(s, i, j):
            try:
                t = term(s, dictionary=self.paradigm.dictionary)
            except TermNotFoundInDictionary:
                t = None

            row = None
            column = None

            if i is not None and j is not None:
                # singular sequence -> table cell
                if self.dim == 2:
                    row = self.rows[i]
                    column = self.columns[j]
                else:
                    column = self.header

            res = Cell(row=row,
                       column=column,
                       coordinate=(i, j),
                       table=self,
                       script=s,
                       term=t)

            if t is not None:
                _terms[t].append(res)

            self._index[s] = res
            return res

        self.header = _cell(self.paradigm.script, None, None)

        if self.dim == 2:
            rows, columns = self.paradigm.headers()
            self.rows = [_cell(s, i, None) for i, s in enumerate(rows)]
            self.columns = [_cell(s, None, j) for j, s in enumerate(columns)]

        self.cells = np.empty(shape=cells.shape, dtype=Cell)
        for i, column in enumerate(cells):
            for j, s in enumerate(column):
                self.cells[i, j] = _cell(s, i, j)

    @property
    def shape(self):
        return self.cells.shape

    def index(self, item):
        return self[item].coordinate

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
        if isinstance(item, Term):
            return item in self.paradigm

        ss = None
        if isinstance(item, Script):
            ss = set(item.singular_sequences)

        # script list set
        if isinstance(item, collections.Iterable) and all(isinstance(ss, Script) for ss in item):
            ss = set(chain.from_iterable(s.singular_sequences for s in item))

        if ss is not None:
            return ss.issubset(self.paradigm.script.singular_sequences)

        raise NotImplemented

    def __iter__(self):
        return map(lambda e: e[()],
                   np.nditer(self.cells, flags=['refs_ok'], op_flags=['readonly']))

    def __getitem__(self, item):
        if isinstance(item, (Script, Term, str)):
            s = script(item)
            return self._index[s]

        if not isinstance(item, collections.Iterable) and self.dim == 1:
            if isinstance(item, int):
                return self.cells[item, 0]
            elif item is None:
                return self.header

        if item[0] is None:
            if item[1] is None:
                return self.header

            if self.dim != 2:
                raise KeyError("No columns in 1d table")
            return self.columns[item[1]]

        elif item[1] is None:
            if self.dim != 2:
                raise KeyError("No rows in 1d table")

            return self.rows[item[0]]
        else:
            return self.cells[item]

    def __str__(self):
        return "<Table %s, (%d, %d)>"%(str(self.paradigm), self.shape[0], self.shape[1])

    def __len__(self):
        return self.shape[0] * self.shape[1]

if __name__ == '__main__':
    from ieml.ieml_objects.terms import term
    t = Table(term('M:O:.M:M:.-'))
    print(t[t.index(term("j.t.-"))].script)
    print(t)
