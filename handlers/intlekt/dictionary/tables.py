from ieml.ieml_objects.terms import term

RELATIONS_CATEGORIES = {
    'inclusion': ['contains', 'contained'],
    'etymology': ['father', 'child'],
    'sibling': ['twin', 'associated', 'crossed', 'opposed']
}

def __build_parallel_table(main_term, parallel_terms):
    """
    Must match the tables geometry
    :param main_term:
    :param parallel_terms:
    :return:
    """
    assert all(len(t.tables) == 1 and t.tables[0].dim == main_term.tables[0].dim and t.tables[0].dim <= 2
               for t in [main_term, *parallel_terms])

    main_tab = main_term.tables[0].tabs[0]
    dim = main_term.tables[0].dim

    headers = {
        'main': str(main_tab.paradigm)
    }

    cells = [
        [
            {
                'main': main_tab.cells[j, i]
            } for j in range(main_tab.cells.shape[0])
        ] for i in range(main_tab.cells.shape[1])
    ]

    columns = [{
        'main': str(main_tab.columns[i])
    } for i in range(main_tab.cells.shape[0])]

    if dim == 2:
        rows = [{
            'main': str(main_tab.rows[i])
        } for i in range(main_tab.cells.shape[1])]
    else:
        rows = []

    return {
        'parent': str(main_term.parent.script) if main_term.parent is not None else None,
        'style': None,
        'dimension': dim, # 1 or 2,

        'header': headers,
        'cells': cells,
        'rows': rows,
        'columns': columns
    }



def get_table_for_term(ieml):
    t = term(ieml)
    # first check if


    tables = [__build_parallel_table(t, [])]

    relations = {
        relcat: {
            reltype: [str(tt.script) for tt in t.relations[reltype]]
            for reltype in RELATIONS_CATEGORIES[relcat] if len(t.relations[reltype]) != 0
        } for relcat in RELATIONS_CATEGORIES
    }

    return {
        'success': True,
        'tables': tables,
        'relations': relations
    }