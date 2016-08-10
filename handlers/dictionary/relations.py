from bidict import bidict

from handlers.dictionary.client import need_login
from handlers.dictionary.commons import terms_db, exception_handler, relation_name_table
from ieml.exceptions import CannotParse
from ieml.operator import sc
from models.relations.relations_queries import RelationsQueries


def get_relation_visibility(body):
    try:
        script_ast = sc(body["ieml"])
        term_db_entry = terms_db().get_term(script_ast)
        inhibited_relations = [relation_name_table.inv[rel_name] for rel_name in term_db_entry["INHIBITS"]]
        return {"viz": inhibited_relations}
    except CannotParse:
        pass


@need_login
@exception_handler
def update_relations(body):
    terms_db().recompute_relations(all_delete=True)
    return {'success': True}


@exception_handler
def get_relations(term):
    script_ast = sc(term["ieml"])
    all_relations = []
    for relation_type, relations in RelationsQueries.relations(script_ast, pack_ancestor=True, max_depth_child=1).items():
        if relations: # if there aren't any relations, we skip
            all_relations.append({
                "reltype" : relation_name_table.inv[relation_type],
                "rellist" :
                    [{"ieml" : rel,
                      "exists": True,
                      "visible": True}
                     for rel in relations]
                    if relation_type != "ROOT" else
                    [{"ieml": relations,
                      "exists": True,
                      "visible": True}],
                "exists" : True,
                "visible" : True
            })
    return all_relations