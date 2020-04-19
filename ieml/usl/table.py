from typing import List

import tqdm

from ieml.dictionary.script import Script
from ieml.usl import USL
from ieml.usl.decoration.path import UslPath
from ieml.usl.usl import usl


class UslTable2D:
    def __init__(self, usl: USL, columns: UslPath, rows: UslPath=None):
        self.usl = usl
        self._rows = rows
        self._columns = columns

        self.paths_structure = dict(self.usl.iter_structure_path_by_script_ss())

    @property
    def columns(self) -> List[USL]:
        """Return a list of paradigms that have as singular sequences the cell columns.
        len(self.rows) == len(self.cells)
        The paradigms are ordered as they will appear in the column tables
        """

        return self._columns.deference(self.usl).singular_sequences

    def column_variations(self, _type):
        """Return a list of the variation that correspond to the dimension of variations of each column"""
        return [c for c in self.columns]

    @property
    def column_paths(self):
        """Return a list of List[(path, ss)], that correspond to the variable path and constant ss of self.columns"""
        return

    @property
    def rows(self):
        """Return a list of paradigms that have as singular sequences the cell row.
        len(self.rows) == len(self.cells)
        The paradigms are ordered as they will appear in the list
        """

        return list(zip(self.path_rows))[1]

    @property
    def row_variations(self):
        """Return a list of the variation that correspond to the dimension of variations of each row"""
        return self.rows

    @property
    def row_paths(self):
        """Return a list of List[(path, ss)], that correspond to the constant path and constant ss of self.rows"""
        return


    @property
    def path_rows(self):
        if self._rows is not None:
            return [(self._rows.as_constant(ss), ss) for ss in self._rows.deference(self.usl).singular_sequences]
        else:
            res = []
            for path, value in self.paths_structure.items():
                if not path.has_prefix(self._columns):
                    res.append((path, value))

            return list(usl(res).singular_sequences.paths_structure.items())

    @property
    def cells(self):
        res = []
        for path, value in self.paths_structure.items():
            if self._rows is None:
                if not path.has_prefix(self._columns) and path.is_constant_path:
                    res.append((path, value))
            else:
                if not path.has_prefix(self._columns) and not path.has_prefix(self._rows):
                    res.append((path, value))

        cells = []
        for row_path, row in tqdm.tqdm(self.path_rows):
            cells_row = []

            for column in self.columns:
                cells_row.append(usl(res +
                                     [(self._columns.as_constant(), column)] +
                                     [(row_path, row)]))

            cells.append(cells_row)

        return cells

