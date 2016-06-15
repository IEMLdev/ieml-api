from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np

_tables = []
Variable = namedtuple('Variable', 'address', 'script')


class Table:

    def __init__(self, row_headers=[], col_headers=[], tab_headers=[], cell_matrix=[]):
        self.headers = [row_headers, col_headers, tab_headers]
        self.cells = cell_matrix


def generate_tables(s):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""

    if isinstance(s, AdditiveScript):
        for child in s.children:
            generate_tables(child)
    elif isinstance(s, MultiplicativeScript):
        plural_vars = [Variable(i, child) for (i, child) in enumerate(s.children) if child.cardinal > 1]
        if len(plural_vars) == 3:
            return _tables.append(build_3d_table(s, plural_vars))
        elif len(plural_vars) == 2:
            return _tables.append(build_2d_table(s))
        elif len(plural_vars) == 1:
            if plural_vars[0].layer == 0:
                return _tables.append(build_1d_table(s))
            else:
                generate_tables(s)


def build_1d_table(s):
    pass


def build_2d_table(s, plural_vars):

    row_headers = []
    col_headers = []

    # Construct the row headers
    if plural_vars[0].address == 0:  # First plural variable is a substance
        row_headers = [MultiplicativeScript(substance=child, attribute=s.children[1], mode=s.children[2])
                       for child in plural_vars[0].script.children]
    elif plural_vars[0].address == 1:  # First plural variable is an attribute
        row_headers = [MultiplicativeScript(substance=s.children[0], attribute=child, mode=s.children[2])
                       for child in plural_vars[0].script.children]
    elif plural_vars[0].address == 2:  # First plural variable is a mode
        row_headers = [MultiplicativeScript(substance=s.children[0], attribute=s.children[1], mode=child)
                       for child in plural_vars[0].script.children]

    # Construct the column headers
    if plural_vars[1].address == 0:  # Second plural variable is a substance
        col_headers = [MultiplicativeScript(substance=child, attribute=s.children[1], mode=s.children[2])
                       for child in plural_vars[1].script.children]
    elif plural_vars[1].address == 1:  # Second plural variable is an attribute
        col_headers = [MultiplicativeScript(substance=s.children[0], attribute=child, mode=s.children[2])
                       for child in plural_vars[1].script.children]
    elif plural_vars[1].address == 2:  # Second plural variable is a mode
        col_headers = [MultiplicativeScript(substance=s.children[0], attribute=s.children[1], mode=child)
                       for child in plural_vars[1].script.children]

    cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)

    return Table(row_headers=row_headers, col_headers=col_headers, cell_matrix=cells)


def build_3d_table(s):
    pass
