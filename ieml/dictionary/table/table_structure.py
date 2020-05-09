import sys
from collections import defaultdict
from itertools import chain

from ieml import error
from ieml.commons import logger
from ieml.dictionary.script import AdditiveScript
from ieml.dictionary.table.table import *

class TableStructure:
    # define a forest of root paradigm
    # This class defines :
    #   - for each paradigm :
    #       o the parent table
    #       o the coordinates of each cells
    # the table structure defines the rank for the paradigms

    def __init__(self, scripts, roots):
        tables, root_paradigms = self._build_tables(roots, scripts)
        self.tables = tables
        self.roots = root_paradigms
        self.table_to_root = {
            **{r: r for r in self.roots},
            **{t: r for r, t_s in self.roots.items() for t in t_s}
        }
        # self.table_to_root = {t: r for r, t_s in self.roots.items() for t in t_s}

    def root(self, s):
        try:
            return self.table_to_root[self.tables[s]]
        except KeyError as e:
            error("No root defined for the script {}".format(str(s)))
            return None


    def __iter__(self):
        yield from self.tables.values()

    def __getitem__(self, item):
        return self.tables[item]

    def __contains__(self, item):
        return item in self.tables

    def children(self, table: Table):
        """
        :param table:
        :return:
        """
        return {t for t in self.tables.values() if t.parent == table}

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
                logger.info("TableStructure._define_root: No parent candidate for the table produced by script %s "
                      "ignoring this script." % (str(s)))
                continue

            if len(candidates) > 1:
                logger.info("TableStructure._define_root: Multiple parent candidate for the table produced by script %s: {%s} "
                      "choosing the smaller one." % (str(s), ', '.join([str(c[0]) for c in candidates])))

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
            if s.singular_sequences[0] not in root_ss:
                logger.error(s.singular_sequences[0] + " not found")
                continue
            roots[root_ss[s.singular_sequences[0]]].append(s)

        root_paradigms = {}
        for root in root_scripts:
            tables, cells = TableStructure._define_root(root=root, paradigms=roots[root])
            root_paradigms[root] = tables | cells

        tables = {}
        for t in chain.from_iterable(root_paradigms.values()):
            tables[t.script] = t
            # if isinstance(t.script, AdditiveScript):
            #     for sub_s in t.script.children:
            #         tables[sub_s] =


        return tables, root_paradigms