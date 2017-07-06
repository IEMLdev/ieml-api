import collections
from itertools import chain
import numpy as np

from .terms import Term
from .script import Script, factorize


class AbstractTable:
    def __init__(self, term, parent):
        self.partitions = None
        self._all_tables = None

        self.term = term

        # parent is always of type Table
        if isinstance(parent, TableSet):
            self.table_set = parent
            self.parent = parent.parent
            self.root_table = parent.root_table

        elif isinstance(parent, Table):
            self.table_set = None
            self.parent = parent
            self.root_table = parent.root_table

        else:
            # root
            self.parent = None
            self.table_set = None
            self.root_table = self
            if term.root != term:
                raise ValueError("Invalid object for root table creation, expected a root term, not %s." % str(term))

        self.all_cells = None
        if self.is_root:
            self.all_cells = {}
            for t_ss in self.term:
                self.all_cells[t_ss] = Cell(term=t_ss, root_table=self)
        else:
            self.all_cells = {t_ss: cell for t_ss, cell in self.root_table.all_cells.items() if t_ss in self.term}

    def get_cells(self, cells):
        return np.vectorize(lambda s: self.all_cells[self.dictionary.terms[s]])(cells)

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

    def __gt__(self, other):
        return self.term.__gt__(other.term)

    def __lt__(self, other):
        return self.term.__lt__(other.term)

    def __getitem__(self, item):
        if len(item) == 1:
            return self.all_cells[item]
        else:
            return self.all_tables[item]

    @property
    def is_root(self):
        return self.term.root == self.term

    @property
    def dictionary(self):
        return self.term.dictionary

    @property
    def regular(self):
        if self.parent.dim == 2:
            if self in self.parent.rows or self in self.parent.columns:
                return True
            else:
                return False
        else:
            return True

    @property
    def rank(self):
        if self.is_root:
            return 0
        elif self.table_set is not None:
            return max(self.table_set.rank, 1)
        elif self.regular:
            return max(self.parent.rank, 1) + 2
        else:
            return max(self.parent.rank, 1) + 1

    @property
    def children(self):
        return chain((self,), chain.from_iterable(p.children for p in self.partitions))

    @property
    def all_tables(self):
        if self._all_tables is None:
            self._all_tables = {table.term: table for table in self.children}
        return self._all_tables

    def accept_term(self, term):
        raise NotImplemented

    def add_paradigm(self, term):
        raise NotImplemented

    def define_paradigm(self, term):
        if not self.is_root:
            self.root_table.define_paradigm(term)

        if not isinstance(term, Term) or len(term) == 1:
            raise ValueError("Unexpected object %s, expected a paradigm Term." % str(term))

        if term in self.all_tables:
            return
            # raise ValueError("Paradigm already defined")

        candidates = []
        for t in self.children:
            if term not in t.term:
                continue

            accept, regular = t.accept_term(term)
            if accept:
                candidates.append((t, regular))

        candidates = sorted(candidates)
        if len(candidates) == 0:
            raise ValueError("No parent candidate for the table produced by term %s" % str(term))

        if len(candidates) > 1:
            print("\t[!] Multiple parent candidate for the table produced by term %s: {%s} choosing the smaller one." %
                  (str(term), ', '.join([str(cand[0].term) for cand in candidates])))

        table = candidates[0][0]
        _table = table.add_paradigm(term)
        self.all_tables[term] = _table


def table(term, parent):
    if term.ntable == 1:
        return Table(term, parent)
    else:
        return TableSet(term, parent)


class Table(AbstractTable):
    def __init__(self, term, parent):
        if term.ntable != 1:
            raise ValueError("Invalid Term for Table creation. Expected a Term paradigm that lead a 2d "
                             "table")

        if parent is not None and not isinstance(parent, AbstractTable):
            raise ValueError("Invalid parameter for parent parameter %s. Expected a Table or TableSet"
                             " instance."%str(parent))

        super().__init__(term=term, parent=parent)
        self.cells = self.root_table.get_cells(term.script.cells[0][:, :, 0])

        assert self.parent is None or isinstance(self.parent, Table)

        self.partitions = set()

        self.dim = 2 if all(s != 1 for s in self.cells.shape) else 1

        if self.dim == 2:
            self.rows = [None] * self.shape[0]
            self.columns = [None] * self.shape[1]

            for i, line in enumerate(self.cells):
                for j, cell in enumerate(line):
                    cell.tables[self] = (i, j)

            for i, row in enumerate(self.cells):
                script_row = factorize([cell.term.script for cell in row])
                if script_row in self.dictionary:
                    self.rows[i] = table(self.dictionary.terms[script_row], self)

            for i, column in enumerate(self.cells.transpose()):
                script_column = factorize([cell.term.script for cell in column])
                if script_column in self.dictionary:
                    self.columns[i] = table(self.dictionary.terms[script_column], self)

            self.partitions = {ts for ts in chain(self.rows, self.columns) if ts is not None}
        else:
            self.cells = self.cells[:,0]
            self.rows = None
            self.columns = None

            for i, cell in enumerate(self.cells):
                cell.tables[self] = (i,)

    def accept_term(self, term):
        """

        :param term:
        :return: is_accepting, is_regular
        """
        def is_connexe_tilling(coords):
            shape_t = self.shape
            # test if the table table is a connexe tiling of the table t
            size = 1
            for i, indexes in enumerate(zip(*coords)):
                # if i >= t.dim:
                #     return False

                indexes = sorted(set(indexes))
                size *= len(indexes)

                missing = [j for j in range(shape_t[i]) if j not in indexes]
                # more than one transition from missing -> included
                transitions = [j for j in missing if (j + 1) % shape_t[i] not in missing]
                if len(transitions) > 1:
                    step = int(shape_t[i] / len(transitions))

                    # check if there is a periodicity
                    if any((j + step)%shape_t[i] not in transitions for j in transitions):
                        return False

                # at least a square of 2x2x1
                if len(indexes) < 2 and i != 2:
                    return False

            if len(coords) == size:
                return True

            return False

        def is_dim_subset(coords):
            """
            Return if it is a dim subset (only one dimension, the others are not touched)
            If True, return (True, nb_dim)
            else (False, 0)

            :param coords:
            :param t:
            :return:
            """
            shape_ts0 = tuple(len(set(indexes)) for indexes in zip(*coords))
            shape_t = self.shape

            if shape_ts0[0] == shape_t[0]:
                return True, shape_ts0[1]

            if shape_ts0[1] == shape_t[1]:
                return True, shape_ts0[0]

            return False, 0

        if self.rank != 0 and self.rank % 2 == 0:
            return False, False

        coords = sorted([self.index(ss) for ss in term])

        if self.dim == 1:
            if len(coords) == coords[-1][0] - coords[0][0] + 1:
                return True, True
            else:
                return False, False

        is_dim, count = is_dim_subset(coords)
        if is_dim and count == 1:
            # one dimension subset, it is a rank 3/5 paradigm
            return True, True

        # the coordinates sorted of the ss of s0 in the table t
        # rank is then 2/4
        if is_connexe_tilling(coords) or is_dim:
            return True, False

        return False, False

    def add_paradigm(self, term):
        _table = table(term, self)
        self.partitions.add(_table)
        return _table

    @property
    def shape(self):
        return self.cells.shape

    # def __getitem__(self, item):
    #     from ieml.ieml_objects.terms import term
    #     if isinstance(item, (Script, Term, str)):
    #         t = term(item, dictionary=self.dictionary)
    #         return self._index[t]
    #
    #     return self.cells[item]

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
        if self.dim == 2:
            return "<Table %s, (%d, %d) - 2D>"%(str(self.term), self.shape[0], self.shape[1])
        else:
            return "<Table %s, (%d,) - 1D>"%(str(self.term), self.shape[0])

    def __len__(self):
        if self.dim == 2:
            return self.shape[0] * self.shape[1]
        else:
            return self.shape[0]


class Cell:
    def __init__(self, term, root_table):
        super().__init__()

        self.term = term
        self.root_table = root_table
        self.tables = {}

    @property
    def rank(self):
        return 6


class TableSet(AbstractTable):
    def __init__(self, term, parent_table):
        super().__init__(term=term, parent=parent_table)

        if term.ntable == 1:
            raise ValueError("Invalid object for TableSet creation, expected a paradigm term that generate multiple "
                             "Table, not %s."%str(term))

        self.partitions = self.tables = {Table(t, self) for t in self.term.tables_term}

        # self.table_set = self

    def accept_term(self, term):
        tables = [table for table in self.tables if table.term in term]

        if len(tables) > 1 and {ss for t in tables for ss in t.term} == set(term.singular_sequences):
            return True, False

        return False, False

    def add_paradigm(self, term):
        _table = table(term, self)

        self.partitions.add(_table)
        if isinstance(_table, Table):
            self.tables.add(_table)

        return _table

    def __str__(self):
        return "<TableSet %s, {%s}>"%(str(self.term), ', '.join([str(t.term) for t in self.partitions]))


if __name__ == '__main__':
    from ieml.ieml_objects.terms import term
    # tt = next(rt.children).columns[0]
    # print(tt.rank)
    root = term("I:")
    rt = table(root, None)

    for t in [t for t in root.relations.contains if len(t) != 1][::-1]:
        rt.define_paradigm(t)


    print(rt)
    ## unit test
    tables = {}
    for root in Dictionary().roots:
        tables[root] = table(root, None)
        for t in [t for t in root.relations.contains if len(t) != 1][::-1]:
            tables[root].define_paradigm(t)

        for _term, _table in tables[root].all_tables.items():
            if _term.rank != _table.rank:
                print("%s | old: %d, new: %d"%(str(_term), _term.rank, _table.rank))


