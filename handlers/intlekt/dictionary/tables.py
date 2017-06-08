from ieml.ieml_objects.tools import term


def get_table_for_term(ieml):
    t = term(ieml)

    tables = t.tables
    relations = t.relations



    return {
        'success': True,
        'tables': tables,
        'relations': relations
    }