from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np

_tables = []
Variable = namedtuple('Variable', ['address', 'script'])
Table = namedtuple('Table', ['headers', 'cells', 'dimension'])


def generate_tables(s, parents=[]):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""

    if isinstance(s, AdditiveScript):
        for child in s.children:
            return generate_tables(child, parents)
    elif isinstance(s, MultiplicativeScript):
        plural_vars = [Variable(i, child) for (i, child) in enumerate(s.children) if child.cardinal > 1]
        if len(plural_vars) == 3:  # We build a 3D table
            return _tables.append(build_table(3, s, plural_vars))
        elif len(plural_vars) == 2:  # We build a 2D table
            return _tables.append(build_table(2, s, plural_vars))
        elif len(plural_vars) == 1:  # we build a 1D table
            if plural_vars[0].script.layer == 0:
                return _tables.append(build_table(1, s, plural_vars))
            else:
                return process_tables(generate_tables(plural_vars[0].script, parents), plural_vars[0].address, s)


def process_tables(tables, address, parent_script):
    """Distributes the sibling multiplications on tables headers and cells"""

    new_tables = []

    # TODO: There's gotta be a better  cleaner way godayum
    if address == 0:  # We need to distribute the multiplication of the attribute and mode of the parent Script
        for table in tables:
            headers = [[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2])
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(script, parent_script.children[1], parent_script.children[2]) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2]) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(script, parent_script.children[1], parent_script.children[2])
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))
    elif address == 1:  # We need to distribute the multiplication of the substance from the right and mode from the left
        for table in tables:
            headers = [[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2])
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(parent_script.children[0], script, parent_script.children[2]) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2]) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(parent_script.children[0], script, parent_script.children[2])
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))
    elif address == 2:  # We need to distribute the multiplication of the substance and the attribute from the right
        for table in tables:
            headers = [[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script)
                        for script in dimension] for dimension in table.headers]
            if table.cells.ndim == 1:
                cells = np.fromiter(
                    [MultiplicativeScript(parent_script.children[0], parent_script.children[1], script) for script in
                     table.cells])
            elif table.cells.ndim == 2:
                cells = np.fromiter(
                    [[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script) for script in
                      row] for row in table.cells])
            elif table.cells.ndim == 3:
                cells = np.fromiter(
                    [[[MultiplicativeScript(parent_script.children[0], parent_script.children[1], script)
                       for script in k] for k in row] for row in table.cells])
            new_tables.append(Table(headers, cells))

    return new_tables


def build_table(dimension, s, plural_vars):

    row_headers = []
    col_headers = []
    tab_headers = []

    cells = np.empty(plural_vars[0].script.cardinal, dtype=object)

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

    if dimension >= 2:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)
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

    if dimension == 3:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal, plural_vars[2].script.cardinal), dtype=object)
        # Construct the tab headers
        if plural_vars[1].address == 0:  # Second plural variable is a substance
            tab_headers = [MultiplicativeScript(substance=child, attribute=s.children[1], mode=s.children[2])
                           for child in plural_vars[2].script.children]
        elif plural_vars[1].address == 1:  # Second plural variable is an attribute
            tab_headers = [MultiplicativeScript(substance=s.children[0], attribute=child, mode=s.children[2])
                           for child in plural_vars[2].script.children]
        elif plural_vars[1].address == 2:  # Second plural variable is a mode
            tab_headers = [MultiplicativeScript(substance=s.children[0], attribute=s.children[1], mode=child)
                           for child in plural_vars[2].script.children]

    for s in row_headers:
        s.check()
    for s in col_headers:
        s.check()
    for s in tab_headers:
        s.check()

    return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, dimension=dimension)


def print_table(t):
    """For debugging purposes"""
    pass
