from collections import namedtuple, OrderedDict

import itertools
import numpy as np
from ieml.script.operator import script

Tab = namedtuple('Tab', ['rows', 'columns', 'paradigm', 'cells'])


class Table:
    def __init__(self, cells):
        if not isinstance(cells, np.ndarray):
            raise ValueError("The cells argument must be an array of singular "
                             "sequences, not %s"%cells.__class__.__name__)

        if len(cells.shape) != 3:
            raise ValueError("Invalid shape for cells")

        self.cells = cells

        self.headers = None
        self.tabs = None
        self.build_headers()

        self.paradigm = script(self.headers)
        self._index = None
        self._dim = None

        self.rank = None
        self.term = None
        self.partition = None

    def define_table(self, term, table=None):
        if not term.defined:
            raise ValueError("Term %s is not defined in the dictionary, can't define a table with it."%str(term))

        self.term = term
        self.rank = term.rank

        if self.rank != 1 and not table.defined:
            raise ValueError("Table is not defined in the dictionary, can't define a table with it as partition."%str(term))

        self.partition = table

    @property
    def defined(self):
        return all(self.__getattribute__(p) is not None for p in ['rank', 'term'])

    def build_headers(self):
        self.headers = {}
        self.tabs = []

        for t in self.cells.transpose(2,0,1):
            rows = [script(c) for c in t]
            columns = [script(c) for c in t.transpose()]
            tabs_sc = script(rows)
            tab = Tab(rows=rows, columns=columns, paradigm=tabs_sc, cells=t)
            self.headers[tabs_sc] = tab
            self.tabs.append(tab)

    def index(self, s):
        if s not in self.paradigm:
            return []

        if self._index is None:
            self._index = {ss: tuple(*zip(*np.where(self.cells == ss))) for ss in self.paradigm.singular_sequences}

        return [self._index[ss] for ss in s.singular_sequences]

    @property
    def dim(self):
        if self._dim is None:
            self._dim = 3
            if self.cells.shape[2] == 1:
                self._dim -= 1

            if self.cells.shape[1] == 1:
                self._dim -= 1

            if self.cells.shape[0] == 1:
                self._dim -= 1

        return self._dim

    def all(self):
        """

        :return: all script referenced in this table
        """
        iter_list = []
        for tab in self.tabs:
            iter_list.append(tab.rows)
            iter_list.append(tab.columns)
            iter_list.append([tab.paradigm])
        iter_list.append(self.cells.flatten())
        iter_list.append([self.paradigm])

        return set(itertools.chain.from_iterable(iter_list))

    def __eq__(self, other):
        return isinstance(other, Table) and self.paradigm == other.paradigm

    def __hash__(self):
        return self.paradigm.__hash__()

