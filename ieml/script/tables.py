from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np

_tables = []
Variable = namedtuple('Variable', ['address', 'script'])
Table = namedtuple('Table', ['headers', 'cells'])


def generate_tables(s, parents=[]):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""

    if isinstance(s, AdditiveScript):
        for child in s.children:
            parents.append(s)
            return generate_tables(child, parents)
    elif isinstance(s, MultiplicativeScript):
        plural_vars = [Variable(i, child) for (i, child) in enumerate(s.children) if child.cardinal > 1]
        if len(plural_vars) == 3:
            return _tables.append(build_3d_table(s, plural_vars, parents))
        elif len(plural_vars) == 2:
            return _tables.append(build_2d_table(s, plural_vars, parents))
        elif len(plural_vars) == 1:
            if plural_vars[0].script.layer == 0:
                return _tables.append(build_1d_table(s, plural_vars, parents))
            else:
                generate_tables(s, parents)


def build_1d_table(s, plural_vars, parents):
    pass


def build_2d_table(s, plural_vars, parents):

    row_headers = []
    col_headers = []
    cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)

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

    for s in row_headers:
        s.check()
    for s in col_headers:
        s.check()

    print(row_headers)
    print(col_headers)

    return Table(headers=[row_headers, col_headers], cells=cells)


def build_3d_table(s, plural_vars, parents):
    pass


def print_table(t):
    """For debugging purposes"""
    
    pass
