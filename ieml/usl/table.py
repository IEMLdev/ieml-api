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
    def columns(self):
        return self._columns.deference(self.usl).singular_sequences

    @property
    def rows(self):
        if self._rows is not None:
            return self._rows.deference(self.usl).singular_sequences
        else:
            res = []
            for path, value in self.paths_structure.items():
                if not path.has_prefix(self._columns):
                    res.append((path, value))

            return usl(res).singular_sequences

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
        for row in tqdm.tqdm(self.rows):
            cells_row = []

            for column in self.columns:
                cells_row.append(usl(res +
                                     [(self._columns.as_constant(), column)] +
                                     ([] if self._rows is None else [(self._rows.as_constant(), row)])))

            cells.append(cells_row)

        return cells

