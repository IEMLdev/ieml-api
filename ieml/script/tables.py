from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np

_tables = []
Variable = namedtuple('Variable', ['address', 'script'])
Table = namedtuple('Table', ['headers', 'cells', 'dimension'])


def generate_tables(parent_script):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""
    global _tables  # TODO: Find a way to not use a global variable

    if isinstance(parent_script, AdditiveScript):
        for child in parent_script.children:
            generate_tables(child)
        return _tables
    elif isinstance(parent_script, MultiplicativeScript):
        # Holds the plural vars of the multiplicative script and their position in the script
        # 0: substance, 1: attribute, 2: mode
        plural_vars = [Variable(i, child) for (i, child) in enumerate(parent_script.children) if child.cardinal > 1]
        if len(plural_vars) == 3:  # We build a 3D table
            _tables.append(_build_table(3, parent_script, plural_vars))
            return _tables
        elif len(plural_vars) == 2:  # We build a 2D table
            _tables.append(_build_table(2, parent_script, plural_vars))
            return _tables
        elif len(plural_vars) == 1:  # we build a 1D table
            if plural_vars[0].script.layer == 0:
                _tables.append(_build_table(1, parent_script, plural_vars))
                return _tables
            else:
                # In this case we need to distribute the from the left or right or both the siblings after we return
                # We do this because we are branching out within a multiplication
                return _process_tables(generate_tables(plural_vars[0].script), plural_vars[0].address, parent_script)


def _process_tables(tables_list, address, parent_script):
    """Distributes the sibling multiplications on tables headers and cells"""
    new_tables = []

    if address == 0:  # We need to distribute the multiplication of the attribute and mode of the parent Script

        operands = {"attribute": parent_script[1], "mode": parent_script[2]}
        for table in tables_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_tables.append(Table(headers, v_dist(table.cells, operands)))

    elif address == 1:  # We need to distribute the multiplication of the substance from the right and mode from the left

        operands = {"substance": parent_script[0], "mode": parent_script[2]}
        for table in tables_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_tables.append(Table(headers, v_dist(table.cells, operands)))

    elif address == 2:  # We need to distribute the multiplication of the substance and the attribute from the right

        operands = {"substance": parent_script[0], "attribute": parent_script[1]}
        for table in tables_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_tables.append(Table(headers, v_dist(table.cells, operands)))

    return new_tables


def _distribute_over_headers(headers, operands):

    new_headers = []

    for dimension in headers:
        dim = []
        for header in dimension:
            if "substance" not in operands:
                operands["substance"] = header
                script = MultiplicativeScript(**operands)
                script.check()
                dim.append(script)
            elif "attribute" not in operands:
                operands["attribute"] = header
                script = MultiplicativeScript(**operands)
                script.check()
                dim.append(script)
            elif "mode" not in operands:
                operands["mode"] = header
                script = MultiplicativeScript(**operands)
                script.check()
                dim.append(script)
        new_headers.append(dim)

    return new_headers


def _distribute_over_cells(cell, operands):

    new_cell = None

    if "substance" not in operands:
        operands["substance"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()
    elif "attribute" not in operands:
        operands["attribute"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()
    elif "mode" not in operands:
        operands["mode"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()

    return new_cell


def _build_table(dimension, multi_script, plural_vars):
    """Constructs the paradigm table and returns it"""
    row_headers = []
    col_headers = []
    tab_headers = []

    if dimension == 1:
        # In this case we only have one header, which is the multiplicative Script given to us
        # that we will expand in the cells array
        cells = np.empty(plural_vars[0].script.cardinal, dtype=object)
        row_headers.append(multi_script)
    if dimension >= 2:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)
        row_headers = _make_headers(plural_vars[0], *multi_script.children)
        col_headers = _make_headers(plural_vars[1], *multi_script.children)
    if dimension == 3:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal, plural_vars[2].script.cardinal), dtype=object)
        tab_headers = _make_headers(plural_vars[2], *multi_script.children)

    _fill_cells(cells, plural_vars, row_headers, col_headers, tab_headers)
    return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, dimension=dimension)


def _fill_cells(cells, plural_vars, row_header, col_header, tab_header):
    """Fills in the cells of the paradigm table by multiplying it's headers"""
    if cells.ndim == 1:
        operands = [row_header[0], row_header[1], row_header[2]]
        for i, child in enumerate(row_header.children):
            operands[plural_vars[0].address] = child
            cells[i] = MultiplicativeScript(*operands)
    elif cells.ndim == 2:
        for i, r_header in enumerate(row_header):
            for j, c_header in enumerate(col_header):
                if plural_vars[0].address == 0 and plural_vars[1].address == 1:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=c_header[1], mode=r_header[2])
                    cells[i][j].check()
                elif plural_vars[0].address == 1 and plural_vars[1].address == 2:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=r_header[1], mode=c_header[2])
                    cells[i][j].check()
                elif plural_vars[0].address == 0 and plural_vars[1].address == 2:
                    cells[i][j] = MultiplicativeScript(substance=r_header[0], attribute=r_header[1], mode=c_header[2])
                    cells[i][j].check()
    elif cells.ndim == 3:
        for i, r_header in enumerate(row_header):
            for j, c_header in enumerate(col_header):
                for k, t_header in enumerate(tab_header):
                    cells[i][j][k] = MultiplicativeScript(substance=r_header[0], attribute=c_header[1], mode=t_header[2])
                    cells[i][j][k].check()


def _make_headers(plural_variable, substance, attribute, mode):
    """Builds the headers for a 2D or 3D paradigm table"""
    operands = [substance, attribute, mode]
    headers = []

    for seq in plural_variable.script.singular_sequences:
        operands[plural_variable.address] = seq
        script = MultiplicativeScript(*operands)
        script.check()
        headers.append(script)
    return headers


if __name__ == "__main__":

    from ieml.parsing.script import ScriptParser

    sp = ScriptParser()
    s = sp.parse("M:.O:.-O:.O:.-B:.T:.n.-'")
    tables = generate_tables(s)
    print(len(tables))
