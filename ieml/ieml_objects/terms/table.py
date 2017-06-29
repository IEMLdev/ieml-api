import collections
from itertools import chain

import numpy as np
from ieml.script.tools import factorize

from ieml.ieml_objects.terms import Term, term, TermNotFoundInDictionary
from ieml.script.script import Script

Cell = collections.namedtuple('Cell', ['tables', 'term', 'root_table'])


class AbstractTable:
    def __init__(self):
        self.children = None
        self.partitions = None
        self.parent = None
        self.table_set = None
        self.term = None
        self.root_table = None

    def __eq__(self, other):
        return isinstance(other, Table) and self.term == other.term

    def __hash__(self):
        return self.term.__hash__()

    def __contains__(self, item):
        if isinstance(item, Term):
            return item in self.term

        ss = None
        if isinstance(item, Script):
            ss = set(item.singular_sequences)

        # script list set
        if isinstance(item, collections.Iterable) and all(isinstance(ss, Script) for ss in item):
            ss = set(chain.from_iterable(s.singular_sequences for s in item))

        if ss is not None:
            return ss.issubset(self.term.script.singular_sequences)

        raise NotImplemented

    @property
    def dictionary(self):
        return self.table_set.dictionary

    @property
    def rank(self):
        raise NotImplemented


class Table(AbstractTable):
    def __init__(self, cells, table_set):
        super().__init__()

        if not isinstance(cells, np.array) or cells.ndim > 2 or cells.dtype != Cell:
            raise ValueError("Invalid cells array for Table creation. Expected a Term paradigm that lead a 2d "
                             "table")
        self.cells = cells

        if not isinstance(table_set, TableSet):
            raise ValueError("Invalid parameter for table set %s. Expected a TableSet instance."%str(table_set))

        self.table_set = table_set

        self.term = self.dictionary.terms[factorize(cell.term.script for cell in self)]

        self.parent = table_set.parent
        self.children = self.partitions = set()
        self.root_table = self.parent.root_table

        self._index = {}

        self.dim = 2 if all(s != 1 for s in cells.shape) else 1
        if self.dim == 2:
            self.rows = [None] * self.shape[0]
            self.columns = [None] * self.shape[1]

            for i, line in self.cells:
                for j, cell in line:
                    cell.tables[self] = (i, j)
                    self._index[cell.term] = cell
        else:
            self.rows = None
            self.columns = None

            for i, cell in self.cells:
                cell.tables[self] = (i,)
                self._index[cell.term] = cell

    @property
    def shape(self):
        return self.cells.shape

    def __getitem__(self, item):
        if isinstance(item, (Script, Term, str)):
            t = term(item, dictionary=self.dictionary)
            return self._index[t]

        return self.cells[item]

    def index(self, item):
        return self[item].tables[self]

    def project(self, elements, key):
        result = {}
        for e in elements:
            result[e] = [c for c in self if key(c.term, e)]

        return result

    def __iter__(self):
        return map(np.asscalar,
                   np.nditer(self.cells, flags=['refs_ok'], op_flags=['readonly']))

    def __str__(self):
        return "<Table %s, (%d, %d)>"%(str(self.term), self.shape[0], self.shape[1])

    def __len__(self):
        if self.dim == 2:
            return self.shape[0] * self.shape[1]
        else:
            return self.shape[0]

    @property
    def rank(self):
        return self.table_set.rank


class TableSet(AbstractTable):
    def __init__(self, term, parent_table):
        super().__init__()

        if not isinstance(term, Term) or len(term) == 1 or term.ntable == 1:
            raise ValueError("Invalid object for TableSet creation, expected a paradigm term that generate multiple "
                             "Table, not %s."%str(term))

        self.parent = parent_table
        self.root_table = self.parent.root_table
        self.term = term
        ## nop nop -->
        self.partitions = self.children = self.tables = \
            {Table(self.root_table.get_cells(cell2d), self) for cell3d in self.term.cells for cell2d in cell3d}

        self.table_set = self

    @property
    def rank(self):
        if self.regular:
            return self.parent.rank + 2
        else:
            return self.parent.rank + 1

    @property
    def regular(self):
        if self.parent.dim == 2:
            if self in self.parent.rows or self in self.parent.columns:
                return True
            else:
                return False
        else:
            return True


class RootTableSet(TableSet):
    def __init__(self, root_term):
        if root_term.root != root_term:
            raise ValueError("Invalid object for root table creation, expected a root term, not %s." % str(root_term))

        self.all_cells = {}
        for t_ss in root_term:
            self.all_cells[t_ss] = Cell(term=t_ss, tables={}, root_table=self)

        super().__init__(root_term, None)

    def add_paradigm(self, term):
        if not isinstance(term, Term) or len(term) == 1:
            raise ValueError("Unexpected object %s, expected a paradigm Term."%str(term))

    def get_cells(self, cells):
        return np.vectorize(lambda t: self.all_cells[t])(cells)

    def rank(self):
        return 1


if __name__ == '__main__':
    from ieml.ieml_objects.terms import term
    t = Table(term('M:O:.M:M:.-'))
    print(t[t.index(term("j.t.-"))].script)
    print(t)
