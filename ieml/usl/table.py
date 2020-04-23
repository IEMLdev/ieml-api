from collections import defaultdict
from itertools import chain, product
from typing import List

import tqdm

from ieml.commons import cached_property
from ieml.dictionary.script import Script
from ieml.usl import USL, PolyMorpheme
from ieml.usl.decoration.path import UslPath, PolymorphemePath, FlexionPath, LexemePath, LexemeIndex
from ieml.usl.usl import usl


class UslTable2D:
    def __init__(self, usl: USL, columns: UslPath, rows: UslPath=None):
        self.usl = usl
        self._rows = rows
        self._columns = columns

        # self.paths_structure = dict(self.usl.iter_structure_path_by_script_ss())

    @cached_property
    def columns(self) -> List[USL]:
        """Return a list of paradigms that have as singular sequences the cell columns.
        len(self.rows) == len(self.cells)
        The paradigms are ordered as they will appear in the column tables
        """

        res = []
        row_variations = [(path, ss) for l in self.row_paths_variation for path, ss in l]

        for column_path_values_list in self.column_paths_constant:
            res.append(usl(self.constant_paths + column_path_values_list + row_variations))

        return res

    @cached_property
    def rows(self) -> List[USL]:
        res = []
        column_variations = [(path, ss) for l in self.column_paths_variation for path, ss in l]

        for row_path_values_list in self.row_paths_constant:
            res.append(usl(self.constant_paths + row_path_values_list + column_variations))

        return res

    @cached_property
    def column_paths_variation(self):
        """Return a list of the variation that correspond to the dimension of variations of each column"""
        res = []
        u = self._columns.deference(self.usl)

        ss_to_groups_path = {ss_v: p.without_morpheme() for p, ss_v in u.iter_structure_path_by_script_ss()}

        for ss in self._columns.deference(self.usl).singular_sequences:
            res.append([(self._columns.concat(ss_to_groups_path[morph], force=False), morph)
                            for path, morph in ss.iter_structure_path_by_script_ss()])

        # return sorted(res, key=lambda l: usl(l + self.constant_paths))
        return sorted(res, key=lambda l: usl([(path.as_constant(vv), vv) for path, vv in l] + self.constant_paths))

    @cached_property
    def column_paths_constant(self):
        """Return a list of List[(path, ss)], that correspond to the variable path and constant ss of self.columns"""
        return [[(p.as_constant(ss), ss) for p, ss in l] for l in self.column_paths_variation]

    @cached_property
    def row_paths_constant(self):
        """Return a list of List[(path, ss)], that correspond to the path and constant ss of self.rows or all the
        dim of variation that are not used by self.columns.
        The path returned as returned as constant."""

        return [[(path.as_constant(morph), morph) for path, morph in l]
                 for l in self.row_paths_variation]

    @cached_property
    def row_paths_variation(self):
        """Return a list of List[(path, ss)], that correspond to the path and constant ss of self.rows or all the
        dim of variation that are not used by self.columns.
        The path returned as returned as constant."""

        constant_dim = set()
        variations_dim = set()
        if self._rows is not None:
            for path, ss in self._rows.deference(self.usl).iter_structure_path_by_script_ss():
                path = self._rows.concat(path.without_morpheme(), force=False)

                if path.deference(self.usl).cardinal != 1:
                    variations_dim.add(path)
                else:
                    constant_dim.add(path)

        else:
            for path, value in self.usl.iter_structure_path_by_script_ss():
                path = path.without_morpheme()

                if not path.has_prefix(self._columns):
                    if path.deference(self.usl).cardinal != 1:
                        variations_dim.add(path.without_morpheme())

        variations = []

        for path_dim in variations_dim:
            bin = []
            for ss in path_dim.deference(self.usl).singular_sequences:
                bin.append([(path_dim.without_morpheme(), morph)
                            for _, morph in ss.iter_structure_path_by_script_ss()])

            variations.append(bin)

        constants = []
        for path_dim in constant_dim:
            for ss in path_dim.deference(self.usl).singular_sequences:
                constants.append((path_dim, ss))


        # group variation by pm for correct ss iteration
        pm_bin = defaultdict(list)
        for path_dim in variations_dim:

            path_head, path_tail = path_dim.split_tail()
            if isinstance(path_tail, (PolymorphemePath)) or \
                (isinstance(path_tail, LexemePath) and path_tail.index == LexemeIndex.FLEXION):
                pm_bin[path_head].extend([(path_tail, ss) for p, ss in path_dim.deference(self.usl).iter_structure_path_by_script_ss()])
        # ss -> group

        # ss_to_group_path = {k: v for k, v in path_bin}


        variations_by_pm = []
        for path_bin, v in pm_bin.items():
            pm_struct = []
            ss_to_groups_path = {ss_v: path_tail for path_tail, ss_v in v}
            for pm_ss in usl(v).singular_sequences:
                group_ss = []
                for _, ss in pm_ss.iter_structure_path_by_script_ss():
                    path = path_bin.concat(ss_to_groups_path[ss])

                    group_ss.append((path, ss))

                pm_struct.append(group_ss)
            variations_by_pm.append(pm_struct)

        # path -> pm
        # variations_by_pm = [[[(path.concat(p_ss), ss) for p_ss, ss in pm_ss.iter_structure_path_by_script_ss()]
        #                         for pm_ss in usl(v).singular_sequences]
        #                         for path, v in pm_bin.items()]

        res = []
        for vars in product(*variations_by_pm):
            # for vars in product(*sorted(variations, reverse=True,
            #                             key=lambda bin: min(ss for v in bin for _, ss in v if not ss.empty))):
            res.append(sum(vars, constants))

        return sorted(res, key=lambda l: usl([(path.as_constant(vv), vv) for path, vv in l] + self.constant_paths))

    @cached_property
    def constant_paths(self):
        res = []

        if self._rows is not None:
            for path, value in self.usl.iter_structure_path_by_script_ss():
                if not path.has_prefix(self._rows) and not path.has_prefix(self._columns):
                    res.append((path, value))
        else:
            for path, value in self.usl.iter_structure_path_by_script_ss():
                if not path.has_prefix(self._columns) and path.is_constant_path:
                    res.append((path, value))

        return res

    @cached_property
    def cells(self):
        cells = []
        for row_path_values_list in tqdm.tqdm(self.row_paths_constant):
            cells_row = []

            for column_path_values_list in self.column_paths_constant:
                cells_row.append(usl(self.constant_paths +
                                     column_path_values_list +
                                     row_path_values_list))

            cells.append(cells_row)

        return cells
