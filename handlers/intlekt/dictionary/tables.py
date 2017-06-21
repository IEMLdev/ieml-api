from ieml.ieml_objects.terms import term

RELATIONS_CATEGORIES = {
    'inclusion': ['contains', 'contained'],
    'etymology': ['father', 'child'],
    'sibling': ['twin', 'associated', 'crossed', 'opposed']
}


def _term_entry(s):
    return {
        'ieml': str(s),
        'fr': term(s).translations.fr,
        'en': term(s).translations.en
    }


def __build_parallel_table(main_term, parallel_terms, others_rel):
    """
    Must match the tables geometry
    :param main_term:
    :param parallel_terms:
    :return:
    """
    assert all(len(t.tables) == 1 and t.tables[0].dim == main_term.tables[0].dim and t.tables[0].dim <= 2
               for t in [main_term, *parallel_terms])

    def _others_rel(s):
        t = term(s)
        return [_term_entry(t.relations[reltype][0].script) for reltype in others_rel]


    main_tab = main_term.tables[0].tabs[0]
    dim = main_term.tables[0].dim

    others_tab = [t.tables[0].tabs[0] for t in parallel_terms]

    headers = {
        'main': _term_entry(main_tab.paradigm),
        'others': [_term_entry(tab.paradigm) for tab in others_tab] + _others_rel(main_tab.paradigm),
        # 'siblings': [_term_entry(t.script) for s]
    }

    cells = [
        [
            {
                'main': _term_entry(main_tab.cells[i, j]),
                'others': [_term_entry(tab.cells[i, j]) for tab in others_tab] + _others_rel(main_tab.cells[i, j])
            } for j in range(main_tab.cells.shape[1])
        ] for i in range(main_tab.cells.shape[0])
    ]

    columns = [{
        'main': _term_entry(main_tab.columns[i]),
        'others': [_term_entry(tab.columns[i]) for tab in others_tab] + _others_rel(main_tab.columns[i])
    } for i in range(main_tab.cells.shape[1])]

    styles = []
    if dim == 2:
        rows = [{
            'main': _term_entry(main_tab.rows[i]),
            'others': [_term_entry(tab.rows[i]) for tab in others_tab] + _others_rel(main_tab.rows[i])
        } for i in range(main_tab.cells.shape[0])]

        ss = main_tab.paradigm
        if ss.children[0] == ss.children[1]:
            styles = ['symmetrical']

    else:
        rows = []

    return {
        'parent': _term_entry(main_term.parent.script) if main_term.parent is not None else None,
        'styles': styles,
        'dimension': dim, # 1 or 2,
        'others_types': ['parallel']*len(parallel_terms) + others_rel,

        'header': headers,
        'cells_lines': cells,
        'rows': rows,
        'columns': columns
    }

def _build_parralel_mapping(t_src, t_dest, reltype):
    # reltype one of ['
    pass


def get_table_for_term(ieml):
    t = term(ieml)

    tables = []
    for table in t.tables:
        # check if term is a tab in a bigger table
        for u_table in t.parent.tables:
            if table.paradigm in u_table.headers:
                upper_table = u_table
                main = term(table.paradigm)
                break
        else:
            upper_table = table
            main = term(table.tabs[0].paradigm)

        others = []
        if upper_table.dim == 3:
            others = [term(tab.paradigm) for tab in upper_table.tabs if tab.paradigm != main.script]

        # todo, add the siblings relationships
        rels = {reltype: {s: term(s).relations[reltype] for s in table.all()}
                for reltype in ['associated', 'opposed', 'crossed']}

        others_rel = [reltype for reltype in rels if all(len(t) == 1 for s, t in rels[reltype].items())]

        tables.append(__build_parallel_table(main, others, others_rel))

    return {
        'success': True,
        'tables': tables,
    }


def get_relations_for_term(ieml):
    t = term(ieml)

    relations = {
        relcat: {
            reltype: [_term_entry(tt.script) for tt in t.relations[reltype]]
            for reltype in RELATIONS_CATEGORIES[relcat] if len(t.relations[reltype]) != 0
        } for relcat in RELATIONS_CATEGORIES
    }

    return {
        'success': True,
        'relations': relations
    }