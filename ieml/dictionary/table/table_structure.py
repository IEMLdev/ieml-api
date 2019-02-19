import sys
from collections import defaultdict
from itertools import chain

from ieml.dictionary.table.table import *


class TableStructure:
    # define a forest of root paradigm
    # This class defines :
    #   - for each paradigm :
    #       o the parent table
    #       o the coordinates of each cells
    # the table structure defines the rank for the paradigms

    def __init__(self, scripts, roots_idx):
        tables, root_paradigms = self._build_tables(scripts[np.where(roots_idx)], scripts)
        self.tables = tables
        self.roots = root_paradigms
        self.table_to_root = {t: r for r, t_s in self.roots.items() for t in t_s}

    def __iter__(self):
        yield from self.tables.values()

    def __getitem__(self, item):
        return self.tables[item]

    @staticmethod
    def _define_root(root, paradigms):
        # add a new root paradigm to the tree structure

        root_table = table_class(root)(root, parent=None)
        tables = {root_table}
        cells = set()

        for ss in root.singular_sequences:
            cell = Cell(script=ss, parent=root_table)
            cells.add(cell)

        defined = {root_table}
        for s in sorted(set(paradigms) - {root}, key=len, reverse=True):
            if s in tables:
                raise ValueError("Already defined")
                # continue

            candidates = set()
            for t in defined:
                accept, regular = t.accept_script(s)
                if accept:
                    candidates |= {(t, regular)}

            if len(candidates) == 0:
                raise ValueError("No parent candidate for the table produced by script %s" % str(s))

            if len(candidates) > 1:
                print("TableStructure._define_root: Multiple parent candidate for the table produced by script %s: {%s} "
                      "choosing the smaller one." % (str(s), ', '.join([str(c[0]) for c in candidates])),
                      file=sys.stderr)

            parent, regular = min(candidates, key=lambda t: t[0].script)

            table = table_class(s)(script=s,
                                           parent=parent,
                                           regular=regular)
            tables.add(table)
            defined.add(table)

        return tables, cells

    @staticmethod
    def _build_tables(root_scripts, scripts):
        roots = defaultdict(list)
        root_ss = {}

        for root in root_scripts:
            for ss in root.singular_sequences:
                root_ss[ss] = root

        # assign each paradigm to its root paradigm
        for s in scripts:
            if s.cardinal == 1:
                continue

            roots[root_ss[s.singular_sequences[0]]].append(s)

        root_paradigms = {}
        for root in root_scripts:
            tables, cells = TableStructure._define_root(root=root, paradigms=roots[root])
            root_paradigms[root] = tables | cells

        tables = {}
        for t in chain.from_iterable(root_paradigms.values()):
            tables[t.script] = t

        return tables, root_paradigms