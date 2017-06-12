from ieml.ieml_objects.terms import Dictionary, term

from handlers.commons import exception_handler
from handlers.dictionary.client import need_login
from handlers.dictionary.commons import relation_name_table, relations_order


@need_login
@exception_handler
def update_relations(body):
    return {'success': True}


@exception_handler
def computation_status():
    return {
        'success': True,
        'free': True
    }


# @exception_handler
def get_relations(ieml, version, factorize_descendant=False):
    t = Dictionary(version).terms[ieml]

    all_relations = [
        {
            "reltype": rel_api,
            "rellist": [
                {
                    "exists": True,
                    "visible": True,
                    "ieml": str(r.script)
                } for r in reversed(t.relations[reltype])
            ],
            "exists": True,
            "visible": True
        } for rel_api, reltype in relation_name_table.items() if reltype != 'ROOT' and t.relations[reltype] != ()
    ]

    all_relations.append({
        "reltype": relation_name_table.inv['ROOT'],
        "rellist": [
            {
                "exists": True,
                "visible": True,
                "ieml": str(t.root.script)
            }],
        "exists": True,
        "visible": True
    })
    return sorted(all_relations, key=lambda rel_entry: relations_order[rel_entry['reltype']])


def get_rel_visibility(ieml, version):
    t = term(ieml, dictionary=version)
    return [relation_name_table.inv[rel] for rel in t.inhibitions]