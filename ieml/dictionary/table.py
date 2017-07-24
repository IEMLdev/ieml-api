import numpy as np

from ieml.commons import cached_property
from ieml.dictionary.script import script
from .terms import Term
from .script import Script, factorize


class Table(Term):
    def __init__(self, script, index, dictionary, parent, regular=False):
        super().__init__(script, index, dictionary, parent)
        self.regular = regular

    @property
    def rank(self):
        if self.parent is None:
            return 0

        if isinstance(self.parent, TableSet):
            return max(self.parent.rank, 1)

        if self.regular:
            return max(self.parent.rank, 1) + 2
        else:
            return max(self.parent.rank, 1) + 1

    @cached_property
    def partitions(self):
        return {t for t in self.relations.contains if isinstance(t, Table) and t.parent == self}


class Cell(Term):
    @property
    def rank(self):
        return 6


class Table2D(Table):
    def __init__(self, script, index, dictionary, parent, regular=False):
        super().__init__(script, index, dictionary, parent, regular)

        if script.tables_script[0] != script or self.script.cells[0].shape[2] != 1 or self.script.cells[0].shape[1] == 1:
            raise ValueError("Invalid script for Table creation: %s. Expected a script that lead a 2d table"%str(script))

        self._index = None

    @property
    def shape(self):
        return self.cells.shape

    @cached_property
    def rows(self):
        return [self.dictionary.terms[row] if row in self.dictionary else None
                for row in self.script_rows]

    @cached_property
    def script_rows(self):
        return [factorize([t.script for t in line]) for line in self.cells]

    @cached_property
    def columns(self):
        return [self.dictionary.terms[column] if column in self.dictionary else None
                for column in self.script_columns]

    @cached_property
    def script_columns(self):
        return [factorize([t.script for t in line]) for line in self.cells.transpose()]

    @cached_property
    def cells(self):
        return np.vectorize(lambda sc: self.dictionary.terms[sc])(self.script.cells[0][:, :, 0])

    def __getitem__(self, item):
        return self.cells[item]

    def index_of(self, item):
        if self._index is None:
            self._index = {
                t.script: index for index, t in np.ndenumerate(self.cells)
            }

        return self._index[script(item)]

    def accept_script(self, script):
        """

        :param term:
        :return: is_accepting, is_regular
        """
        def is_connexe_tilling(coords):
            shape_t = self.shape
            # test if the table table is a connexe tiling of the table t
            size = 1
            for i, indexes in enumerate(zip(*coords)):

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

        if script not in self.script:
            return False, False

        if self.rank != 0 and self.rank % 2 == 0:
            return False, False

        coords = sorted([self.index_of(ss) for ss in script.singular_sequences])

        is_dim, count = is_dim_subset(coords)
        if is_dim and count == 1:
            # one dimension subset, it is a rank 3/5 paradigm
            return True, True

        # the coordinates sorted of the ss of s0 in the table t
        # rank is then 2/4
        if is_connexe_tilling(coords) or is_dim:
            return True, False

        return False, False


class Table1D(Table):
    def __init__(self, script, index, dictionary, parent, regular=False):
        super().__init__(script, index, dictionary, parent, regular)
        self._index = None

    @property
    def shape(self):
        return self.cells.shape

    @cached_property
    def cells(self):
        return np.vectorize(lambda sc: self.dictionary.terms[sc])(self.script.cells[0][:, 0, 0])

    def __getitem__(self, item):
        return self.cells[item]

    def index_of(self, item):
        if self._index is None:
            self._index = {
                t.script: index for index, t in np.ndenumerate(self.cells)
            }

        return self._index[script(item)]

    def accept_script(self, script):
        if script not in self.script:
            return False, False

        coords = sorted([self.index_of(ss) for ss in script.singular_sequences])

        if len(coords) == coords[-1][0] - coords[0][0] + 1:
            return True, True
        else:
            return False, False


class TableSet(Table):
    def __init__(self, script, index, dictionary, parent, regular=False):
        super().__init__(script, index, dictionary, parent, regular)

        if len(self.script.tables_script) == 1:
            raise ValueError("Invalid script for TableSet creation: %s. Expected a script that generate multiple "
                             "Tables"%str(script))

    @property
    def tables(self):
        return [self.dictionary.terms[s] for s in self.script.tables_script]

    def accept_script(self, script):
        """
        True when the term is a subset of this term tables. If the parent of this term is already a TableSet,return
        always false (only one main tableset)
        :param term:
        :return:
        """
        if isinstance(self.parent, TableSet):
            return False, False

        tables = [table for table in self.script.tables_script if table in script]

        if len(tables) >= 1 and {ss for t in tables for ss in t.singular_sequences} == set(script.singular_sequences):
            return True, False

        return False, False


class Table3D(TableSet):
    def __init__(self, script, index, dictionary, parent, regular=False):
        super().__init__(script, index, dictionary, parent, regular)

    def __getitem__(self, item):
        return self.tables[item[0]][item[1:]]


def table_class(script):
    if len(script) == 1:
        return Cell

    if len(script.tables_script) == 1:
        dim = sum(1 for s in script.cells[0].shape if s != 1)
        if dim == 1:
            return Table1D
        if dim == 2:
            return Table2D

        raise ValueError("Invalid dim %d for script %s"%(dim, str(script)))
    else:
        if len(script.cells) == 1:
            return Table3D
        else:
            return TableSet
