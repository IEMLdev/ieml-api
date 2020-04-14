from ieml.dictionary.script import Script
from ieml.usl import USL
from ieml.usl.decoration.path import UslPath
from ieml.usl.usl import usl


class UslTable2D:
    def __init__(self, usl: USL, rows: UslPath, columns: UslPath):
        self.usl = usl
        self._rows = rows
        self._columns = columns

        self.paths_structure = dict(self.usl.iter_structure_path_by_type(Script))

    @property
    def columns(self):
        return self._columns.deference(self.usl).singular_sequences

    @property
    def rows(self):
        return self._rows.deference(self.usl).singular_sequences

    @property
    def cells(self):
        res = []
        for path, value in self.paths_structure.items():
            if not path.has_prefix(self.columns) and not path.has_prefix(self.rows):
                res.append((path, value))

        cells = []
        for row in self.rows:
            cells_row = []
            for column in self.columns:
                cells_row.append(usl(res +\
                                     [(self._rows, row)] +\
                                     [(self._columns, column)]))

            cells.append(cells_row)

        return cells

