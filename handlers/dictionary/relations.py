from bidict import bidict

from handlers.dictionary.client import need_login
from handlers.dictionary.commons import script_parser, terms_db
from ieml.exceptions import CannotParse
from ieml.script.constants import OPPOSED_SIBLING_RELATION, ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, \
    TWIN_SIBLING_RELATION, FATHER_RELATION, SUBSTANCE, ATTRIBUTE, MODE, CHILD_RELATION, CONTAINED_RELATION, \
    CONTAINS_RELATION
from models.relations.relations_queries import RelationsQueries

relation_name_table = bidict({
    "Crossed siblings": CROSSED_SIBLING_RELATION,
    "Associated siblings": ASSOCIATED_SIBLING_RELATION,
    "Twin siblings": TWIN_SIBLING_RELATION,
    "Opposed siblings": OPPOSED_SIBLING_RELATION,

    "Ancestors in mode": FATHER_RELATION + '.' + MODE,
    "Ancestors in attribute": FATHER_RELATION + '.' + ATTRIBUTE,
    "Ancestors in substance": FATHER_RELATION + '.' + SUBSTANCE,

    "Descendents in mode": CHILD_RELATION + '.' + MODE,
    "Descendents in attribute": CHILD_RELATION + '.' + ATTRIBUTE,
    "Descendents in substance": CHILD_RELATION + '.' + SUBSTANCE,


    "Contained in": CONTAINED_RELATION,
    "Belongs to Paradigm": 'ROOT',
    "Contains": CONTAINS_RELATION
})


def get_relation_visibility(body):
    try:
        script_ast = script_parser.parse(body["ieml"])
        term_db_entry = terms_db.get_term(script_ast)
        inhibited_relations = [relation_name_table.inv[rel_name] for rel_name in term_db_entry["INHIBITS"]]
        return {"viz": inhibited_relations}
    except CannotParse:
        pass


@need_login
def add_relation_visiblity(body):
    added_inibitions_set = set(relation_name_table[relation] for relation in body["relations"])
    current_relations_set = set(terms_db.get_term(body["ieml"])["INHIBITS"])
    new_set = added_inibitions_set.intersection(current_relations_set)
    try:
        script_ast = script_parser.parse(body["ieml"])
        terms_db.update_term(script_ast, inhibits=list(new_set))
    except CannotParse:
        pass


@need_login
def remove_relation_visibility(body):
    try:
        script_ast = script_parser.parse(body["ieml"])
        terms_db.update_term(script_ast, inhibits=list())
    except CannotParse:
        pass


def get_relations(term):
    try:
        script_ast = script_parser.parse(term["ieml"])
        all_relations = []
        for relation_type, relations in RelationsQueries.relations(script_ast, pack_ancestor=True).items():
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
    except CannotParse:
        pass # TODO : maybe define an error