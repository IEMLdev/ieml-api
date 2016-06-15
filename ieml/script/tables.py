

def generate_tables(s):
    """Generates a paradigm table from a given Script. The table is implemented using a named tuple"""

    if s.level == 'ADDITIVESCRIPT':
        for child in s.children:
            generate_tables(child)

    elif s.level == 'MULTIPLICATIVESCRIPT':

        singular_vars_count = count_singular_variables(s)
        if singular_vars_count == 0:
            build_3d_table(s)
        elif singular_vars_count == 1:
            build_2d_table(s)
        elif singular_vars_count == 2:
            pass


def build_3d_table(s):

    pass

def build_2d_table(s):

    pass

def count_singular_variables(s):

    count = 0
    for child in s.children:
        if child.cardinal == 1:
            count += 1
    return count