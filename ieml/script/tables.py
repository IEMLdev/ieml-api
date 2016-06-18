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


def build_table(dimension, multi_script, plural_vars):
    row_headers = []
    col_headers = []
    tab_headers = []

    cells = np.empty(plural_vars[0].script.cardinal, dtype=object)
    row_headers = make_headers(*multi_script.children, plural_variable=plural_vars[0])

    if dimension >= 2:  # Construct the column headers
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)
        col_headers = make_headers(*multi_script.children, plural_variable=plural_vars[1])

    if dimension == 3:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal, plural_vars[2].script.cardinal), dtype=object)
        tab_headers = make_headers(*multi_script.children, plural_variable=plural_vars[2])

    return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, dimension=dimension)


def make_headers(substance, attribute, mode, plural_variable=None):

    arg_list = [substance, attribute, mode]
    headers = []

    for child in plural_variable.script.children:
        arg_list[plural_variable.address] = child
        script = MultiplicativeScript(*arg_list)
        script.check()
        headers.append(script)
    return headers


def print_table(t):
    """For debugging purposes"""
    pass
