from handlers.commons import exception_handler
from handlers.dictionary.client import need_login
from handlers.dictionary.commons import relation_name_table, relations_order

from ieml.exceptions import CannotParse
from ieml.ieml_objects.tools import term


def get_relation_visibility(body):
    try:
        print("get_relation_visibility")
        _term = term(body["ieml"])
        inhibited_relations = [relation_name_table.inv[rel_name] for rel_name in _term.inhibitions]
        return {"viz": inhibited_relations}
    except CannotParse:
        pass


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
def get_relations(body):
    t = term(body["ieml"])

    relations = list(t.relations)
    _relations = []
    for l in relations:
        if l == [] or isinstance(l[0], Term):
            _relations.append(l)
        else:
            _relations.extend(l)

    all_relations = [
        {
            "reltype": relation_name_table.inv[RELATION_TYPES_TO_INDEX.inv[i]],
            "rellist": [
                {
                    "exists": True,
                    "visible": True,
                    "ieml": str(r.script)
                } for r in reversed(rels)
            ],
            "exists": True,
            "visible": True
        } for i, rels in enumerate(_relations) if rels != []
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
