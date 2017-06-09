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

    others_tab = [t.tables[0].tabs[0] for t in parallel_terms]

    headers = {
        'main': str(main_tab.paradigm),
        'others': [str(tab.paradigm) for tab in others_tab]
    }

    cells = [
        [
            {
                'main': str(main_tab.cells[i, j]),
                'others': [str(tab.cells[i, j]) for tab in others_tab]
            } for j in range(main_tab.cells.shape[1])
        ] for i in range(main_tab.cells.shape[0])
    ]

    columns = [{
        'main': str(main_tab.columns[i]),
        'others': [str(tab.columns[i]) for tab in others_tab]
    } for i in range(main_tab.cells.shape[1])]

    styles = []
    if dim == 2:
        rows = [{
            'main': str(main_tab.rows[i]),
            'others': [str(tab.rows[i]) for tab in others_tab]
        } for i in range(main_tab.cells.shape[0])]

        ss = main_tab.paradigm
        if ss.children[0] == ss.children[1]:
            styles = ['symmetrical']

    else:
        rows = []

    return {
        'parent': str(main_term.parent.script) if main_term.parent is not None else None,
        'styles': styles,
        'dimension': dim, # 1 or 2,

        'header': headers,
        'cells_lines': cells,
        'rows': rows,
        'columns': columns
    }



def get_table_for_term(ieml):
    t = term(ieml)
    # first check if

    relations = {
        relcat: {
            reltype: [str(tt.script) for tt in t.relations[reltype]]
            for reltype in RELATIONS_CATEGORIES[relcat] if len(t.relations[reltype]) != 0
        } for relcat in RELATIONS_CATEGORIES
    }

    tables = []
    for table in t.tables:
        main = term(table.tabs[0].paradigm)
        if table.dim == 3:
            others = [term(tab.paradigm) for tab in  table.tabs[1:]]
        else:
            # todo, add the siblings relationships
            others = []

        tables.append(__build_parallel_table(main, others))

    return {
        'success': True,
        'tables': tables,
        'relations': relations
    }