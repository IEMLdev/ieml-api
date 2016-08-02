from ieml.script import AdditiveScript, MultiplicativeScript
from collections import namedtuple
import numpy as np
from models.relations.relations import RelationsConnector
from ieml.script.tools import factorize
from ieml.operator import sc

Variable = namedtuple('Variable', ['address', 'script'])
Table = namedtuple('Table', ['headers', 'cells', 'paradigm'])


def generate_tables(parent_script):
    """Generates a paradigm table from a given Script.
       The table is implemented using a named tuple"""
    table_list = []

    if isinstance(parent_script, AdditiveScript):
        if parent_script.layer == 0:
            table_list.append(_build_table(1, parent_script, parent_script))
            return table_list
        else:
            for child in parent_script.children:
                table_list.extend(generate_tables(child))
            return table_list
    elif isinstance(parent_script, MultiplicativeScript):
        # Holds the plural vars of the multiplicative script and their position in the script
        # 0: substance, 1: attribute, 2: mode
        plural_vars = [Variable(i, child) for (i, child) in enumerate(parent_script.children) if child.cardinal > 1]
        if len(plural_vars) == 3:  # We build a 3D table
            table_list.append(_build_table(3, parent_script, plural_vars))
            return table_list
        elif len(plural_vars) == 2:  # We build a 2D table
            table_list.append(_build_table(2, parent_script, plural_vars))
            return table_list
        elif len(plural_vars) == 1:  # we build a 1D table
            if plural_vars[0].script.layer == 0:
                table_list.append(_build_table(1, parent_script, plural_vars))
                return table_list
            else:
                # In this case we need to distribute the from the left or right or both the siblings after we return
                # We do this because we are branching out within a multiplication
                table_list.extend(_process_tables(generate_tables(plural_vars[0].script), plural_vars[0].address,
                                                  parent_script))
                return table_list


def _process_tables(table_list, address, parent_script):
    """Distributes the sibling multiplications on tables headers and cells"""
    new_tables = []

    if address == 0:  # We need to distribute the multiplication of the attribute and mode of the parent Script

        operands = {"attribute": parent_script[1], "mode": parent_script[2]}
        for table in table_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_paradigm = MultiplicativeScript(substance=table.paradigm, **operands)
            new_paradigm.check()
            new_tables.append(Table(headers, v_dist(table.cells, operands), new_paradigm))

    elif address == 1:  # We need to distribute the multiplication of the substance from the right and mode from the left

        operands = {"substance": parent_script[0], "mode": parent_script[2]}
        for table in table_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_paradigm = MultiplicativeScript(attribute=table.paradigm, **operands)
            new_paradigm.check()
            new_tables.append(Table(headers, v_dist(table.cells, operands), new_paradigm))

    elif address == 2:  # We need to distribute the multiplication of the substance and the attribute from the right

        operands = {"substance": parent_script[0], "attribute": parent_script[1]}
        for table in table_list:
            headers = _distribute_over_headers(table.headers, operands)
            v_dist = np.vectorize(_distribute_over_cells)
            new_paradigm = MultiplicativeScript(mode=table.paradigm, **operands)
            new_paradigm.check()
            new_tables.append(Table(headers, v_dist(table.cells, operands), new_paradigm))

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
                del operands["substance"]
            elif "attribute" not in operands:
                operands["attribute"] = header
                script = MultiplicativeScript(**operands)
                script.check()
                dim.append(script)
                del operands["attribute"]
            elif "mode" not in operands:
                operands["mode"] = header
                script = MultiplicativeScript(**operands)
                script.check()
                dim.append(script)
                del operands["mode"]
        new_headers.append(dim)

    return new_headers


def _distribute_over_cells(cell, operands):

    new_cell = None

    if "substance" not in operands:
        operands["substance"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()
        del operands["substance"]
    elif "attribute" not in operands:
        operands["attribute"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()
        del operands["attribute"]
    elif "mode" not in operands:
        operands["mode"] = cell
        new_cell = MultiplicativeScript(**operands)
        new_cell.check()
        del operands["mode"]

    return new_cell


def _build_table(dimension, parent_script, plural_vars):
    """Constructs the paradigm table and returns it"""
    row_headers = []
    col_headers = []
    tab_headers = []

    if dimension == 1:
        if isinstance(plural_vars, AdditiveScript):
            cells = np.empty(plural_vars.cardinal, dtype=object)
            row_headers.append(parent_script)
            for i, child in enumerate(plural_vars.children):
                cells[i] = child
            return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, paradigm=parent_script)
        else:
            # In this case we only have one header, which is the multiplicative Script given to us
            # that we will expand in the cells array
            cells = np.empty(plural_vars[0].script.cardinal, dtype=object)
        row_headers.append(parent_script)
    if dimension >= 2:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal), dtype=object)
        row_headers = _make_headers(plural_vars[0], *parent_script.children)
        col_headers = _make_headers(plural_vars[1], *parent_script.children)
    if dimension == 3:
        cells = np.empty((plural_vars[0].script.cardinal, plural_vars[1].script.cardinal, plural_vars[2].script.cardinal), dtype=object)
        tab_headers = _make_headers(plural_vars[2], *parent_script.children)

    _fill_cells(cells, plural_vars, row_headers, col_headers, tab_headers)
    return Table(headers=[row_headers, col_headers, tab_headers], cells=cells, paradigm=parent_script)


def _fill_cells(cells, plural_vars, row_headers, col_headers, tab_header):
    """Fills in the cells of the paradigm table by multiplying it's headers"""
    if cells.ndim == 1:
        # We only have one rwo header in this case and it's row_headers[0]
        operands = [row_headers[0][0], row_headers[0][1], row_headers[0][2]]
        for i, child in enumerate(plural_vars[0].script.children):
            # Since it's one dimensional, we only need to check the first (and only) plural variable and expand it.
            operands[plural_vars[0].address] = child
            cells[i] = MultiplicativeScript(*operands)
            cells[i].check()
    elif cells.ndim == 2:
        for i, r_header in enumerate(row_headers):
            for j, c_header in enumerate(col_headers):
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
        for i, r_header in enumerate(row_headers):
            for j, c_header in enumerate(col_headers):
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


def print_headers(headers, debug=True):
    """Print headers for debugging purposes"""
    dimensions = ['row_headers', 'col_headers', 'tab_headers']

    if debug:
        for title, dim in zip(dimensions, headers):
            print(title + " = [", end=" ")
            for elem in dim:
                print("self.parser.parse(\"" + str(elem) + "\"),", end=" ")
            print(']')
    else:
        for title, dim in zip(dimensions, headers):
            print(title + " = [", end=" ")
            for elem in dim:
                print(str(elem), end=" ")
            print(']')


def print_cells(cells):
    """Print table cells for debugging purposes"""

    if cells.ndim == 1:
        for i, cell in enumerate(cells):
            print("cells[" + str(i) + "] = " + "self.parser.parse(\"" + str(cell) + "\")")
    elif cells.ndim == 2:
        for i, row in enumerate(cells):
            for j, cell in enumerate(row):
                print("cells[" + str(i) + "][" + str(j) + "] = " + "self.parser.parse(\"" + str(cell) + "\")")
    elif cells.ndim == 3:
        for k in range(cells.shape[2]):
            for i, row in enumerate(cells):
                for j, col in enumerate(row):
                    print("cells[" + str(i) + "][" + str(j) + "][" + str(k) + "] = " + "self.parser.parse(\"" + str(cells[i][j][k]) + "\")")
            print('\n')


def get_table_rank(paradigm):
    """
        This method will compute the rank of the table associated to the paradigm given as input

        :param paradigm: An IEML paradigm term
        :return: The rank of the table associated with the paradigm as an integer from 1 to 5
        """
    rc = RelationsConnector()
    paradigm_rel = rc.get_script(paradigm)

    # TODO: Check if the paradigm was found in the database
    if paradigm_rel["TYPE"] == "ROOT_PARADIGM":  # Root paradigms have a rank 1
        return 1

    return _compute_rank(paradigm, rc.get_script(paradigm_rel['ROOT']))


def _compute_rank(paradigm, root):
    """
            Rank 1
            /     \
           /       \
       Rank 2     Rank 3
                  /    \
                 /      \
             Rank 4    Rank 5
    Parameters
    ----------
    paradigm
    root

    Returns
    -------

    """
    if isinstance(root, dict):
        root = sc(root["_id"])

    tbls = _get_tables(root, paradigm.singular_sequences)  # We get the tables that contain our paradigm
    coordinates = _get_seq_coordinates(paradigm.singular_sequences, tbls)

    if len(tbls) == 1:
        # We are checking if only one header for the root table was used to create the child paradigm
        check_dim = [len(dim_coord) == 1 for dim_coord in coordinates[tbls[0].paradigm]]
    if len(tbls) == 1 and any(check_dim):  # In this case the paradigm has at least a rank of 3
        # now we check if it has, in fact, a rank for 3, or either 4 or 5.
        # We start by getting the header that contain our paradigms singular sequences
        header = tbls[0].headers[check_dim.index(True)][coordinates[tbls[0].paradigm][check_dim.index(True)][0]]
        if header.singular_sequences == paradigm.singular_sequences:
            # In this case the header is actually our paradigm and we're done. (It has a rank of 3)
            return 3
        # Otherwise, it has a rank of either 4 or 5
        elif _is_sublist(paradigm.singular_sequences, header.singular_sequences):
            # TODO: I don't think we really need to check that condition.
            # We need to build the table associated with the header (which is a paradigm) of rank 3
            tbls = _get_tables(header, paradigm.singular_sequences)
            coordinates = _get_seq_coordinates(paradigm.singular_sequences, tbls)
            if len(tbls) == 1 and any(len(dim_coord) == 1 for dim_coord in coordinates[tbls[0].paradigm]):
                return 5
            else:
                return 4
    else:
        # otherwise if the paradigm is constructed from more than one header then it's of rank 2
        return 2


def _get_seq_coordinates(singular_sequences, tables):
    """

    Parameters
    ----------
    singular_sequences
    tables

    Returns
    -------
    list: numpy arrays containing the coordinates in the table of all the singular sequences.
          coords = [array(), array(), array()] where coords[0] and row indices, coords[1] are column indices, coords[2]
          are tab indices.

    """

    coordinates = {table.paradigm: [] for table in tables}

    for table in tables:
        coords = [np.empty(0, dtype=int) for i in range(3)]
        for seq in singular_sequences:
            if isinstance(seq, str):
                seq = sc(seq)
            if seq in table.cells:
                coord = np.where(table.cells == seq)
                for i, coordinate in enumerate(coord):
                    coords[i] = np.append(coords[i], coordinate)
        # remove the empty index arrays inside coordinates
        coordinates[table.paradigm] = [np.unique(coord) for coord in coords if len(coord) > 0]

    return coordinates


def _get_tables(root, singular_sequences):
    """

    Parameters
    ----------
    root
    singular_sequences

    Returns
    -------
    The root tables that contain the singular sequences of the paradigm for which we're computing the rank
    """
    if isinstance(root, dict):
        root = sc(root["_id"])

    # Intersection of tables of the same paradigm are always empty
    # So candidates contains tables that partition of our singular_sequences
    candidates = [table for table in generate_tables(root)
                  if set(singular_sequences) & set(table.paradigm.singular_sequences)]
    return candidates


def _is_sublist(small_list, big_list):
    """

    Parameters
    ----------
    small_list
    big_list

    Returns
    -------
    A boolean indicating if the elements of small_list are a subset of the elements in big_list
    """

    return all(elem in big_list for elem in small_list)

if __name__ == "__main__":

    from ieml.parsing.script import ScriptParser

    sp = ScriptParser()
    s = sp.parse("m.-M:O:.-'m.-M:O:.-',E:A:S:.-',+E:A:T:.-',E:.-',+E:A:T:.-',+s.o.-m.o.-',_")
    tables = generate_tables(s)
    print(len(tables))
