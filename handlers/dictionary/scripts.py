from ieml.operator import sc
from models.exceptions import DBException, InvalidRelationCollectionState
from models.relations.relations_queries import RelationsQueries
from ..caching import cached, flush_cache
from handlers.dictionary.commons import terms_db, exception_handler
from ieml.exceptions import CannotParse
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from ieml.script.script import MultiplicativeScript, NullScript
from ieml.script.tables import generate_tables
from ieml.script.tools import old_canonical
from .client import need_login


@cached("all_ieml", 60)
@exception_handler
def all_ieml():
    """Returns a dump of all the terms contained in the DB, formatted for the JS client"""
    def _build_old_model_from_term_entry(term_db_entry):
        terms_ast = sc(term_db_entry["_id"])
        try:
            rank = RelationsQueries.rank(term_db_entry["_id"]) if terms_ast.paradigm else 0
        except InvalidRelationCollectionState:
            rank = 'n/a'

        return {
            "_id" : term_db_entry["_id"],
            "IEML" : term_db_entry["_id"],
            "CLASS" : terms_ast.script_class,
            "EN" : term_db_entry["TAGS"]["EN"],
            "FR" : term_db_entry["TAGS"]["FR"],
            "PARADIGM" : "1" if terms_ast.paradigm else "0",
            "LAYER" : terms_ast.layer,
            "TAILLE" : terms_ast.cardinal,
            "CANONICAL" : old_canonical(terms_ast),
            "ROOT_PARADIGM" : term_db_entry["ROOT"],
            "RANK": rank
        }

    result = [_build_old_model_from_term_entry(entry) for entry in terms_db().get_all_terms()]
    return result


def parse_ieml(iemltext):
    try:
        script_ast = sc(iemltext)
        return {
            "success" : True,
            "level" : script_ast.layer,
            "taille" : script_ast.cardinal,
            "class" : script_ast.script_class, # TODO : change it to the actual value
            "canonical" : old_canonical(script_ast)
        }
    except CannotParse:
        return {"success" : False,
                "exception" : "Invalid script"}


def script_table(iemltext):
    class_to_color = {
        AUXILIARY_CLASS: 'auxiliary',
        VERB_CLASS: 'verb',
        NOUN_CLASS: 'noun'
    }

    class_to_header_color = {k: 'header-'+class_to_color[k] for k in class_to_color}

    def _table_entry(col_size=0, ieml=None, header=False, top_header=False):
        '''
        header + ieml + !top_header = colomn and line header
        header + ieml + top_header = top header
        !ieml + top_header = gray square -_-'
        ieml + !header = cell

        :param ieml:
        :param auto_color:
        :param header:
        :param top_header:
        :return:
        '''
        if not ieml:
            color = 'black'
        elif not header:
            color = class_to_color[ieml.script_class]
        else:
            color = class_to_header_color[ieml.script_class]

        return {
            'background': color,
            'value': str(ieml) if ieml else '',
            'means': {'fr': '', 'en': ''},
            'creatable': False,
            'editable': bool(ieml),
            'span': {
                'col': col_size if header and top_header and ieml else 1,
                'row': 1
            }
        }

    def _slice_array(table, col=False, dim=None, tab_header=None):
        if col:
            result = [
                _table_entry(1, ieml=tab_header if tab_header else table.headers[0][0], header=True, top_header=True)
            ]
            result.extend([_table_entry(ieml=e) for e in table.cells])

        elif dim is None:
            col_size = len(table.headers[1])

            result = [
                _table_entry(col_size + 1, ieml=tab_header if tab_header else table.paradigm, header=True,
                             top_header=True),
                _table_entry(top_header=True)  # grey square
            ]

            for col in table.headers[1]:
                result.append(_table_entry(ieml=col, header=True))

            for i, line in enumerate(table.cells):
                result.append(_table_entry(ieml=table.headers[0][i], header=True))
                for cell in line:
                    result.append(_table_entry(ieml=cell))
        else:
            col_size = len(table.headers[1][0])

            result = [
                _table_entry(col_size + 1, ieml=tab_header if tab_header else table.paradigm, header=True, top_header=True),
                _table_entry(top_header=True)  # grey square
            ]

            for col in table.headers[1][dim]:
                result.append(_table_entry(ieml=col, header=True))

            for i, line in enumerate(table.cells[dim]):
                result.append(_table_entry(ieml=table.headers[0][dim][i], header=True))
                for cell in line:
                    result.append(_table_entry(ieml=cell[0]))

        return result

    def _build_tables(tables):
        result = []
        for table in tables:
            tabs = []
            if table.dimension != 3:
                result.append({
                    'Col': len(table.headers[1]) + 1,
                    'table': [{
                        'tabTitle': '',
                        'slice': _slice_array(table, col=table.dimension == 1)
                    }]
                })
            else:
                # if the table is 3D, we don't want a true 3D table
                table.split_tabs = True

                # multiple tabs
                for i, tab in enumerate(table.headers[2]):
                    tabs.append({
                        'tabTitle': str(tab),
                        'slice': _slice_array(table, dim=i, tab_header=tab)
                    })

                result.append({
                    'Col': len(table.headers[1][0]) + 1,
                    'table': tabs
                })

        return result

    try:
        script_ast = sc(iemltext)
        tables = generate_tables(script_ast)

        if tables is None:
            return {
                'exception': 'not enough variables to generate table',
                'at': 7,
                'success': False
            }
        return {
            'tree': {
                'input': str(script_ast),
                'Tables': _build_tables(tables)
            },
            'success': True
        }
    except CannotParse:
        pass


def script_tree(iemltext):
    def _tree_entry(script):
        if script.layer == 0:
            return {
                'op': 'none',
                'name': str(script),
                'children': []
            }

        if isinstance(script, NullScript):
            n = NullScript(script.layer - 1)
            return {
                'op': '*',
                'name': str(script),
                'children': [
                    _tree_entry(n) for i in range(3)
                ]
            }
        return {
            'op': '*' if isinstance(script, MultiplicativeScript) else '+',
            'name': str(script),
            'children': [
                _tree_entry(s) for s in script
            ]
        }

    try:
        script = sc(iemltext)
        return {
            'level': script.layer,
            'tree': _tree_entry(script),
            'taille': script.cardinal,
            'success': True,
            'canonical': old_canonical(script)
        }
    except CannotParse:
        pass


@need_login
@flush_cache
@exception_handler
def new_ieml_script(body):
    script_ast = sc(body["IEML"])
    terms_db().add_term(script_ast,  # the ieml script's ast
                      {"FR": body["FR"], "EN": body["EN"]},  # the
                      [], # no inhibitions at the script's creation
                      root=body["PARADIGM"] == "1", recompute_relations=False)
    return { "success" : True, "IEML" : str(script_ast)}


@need_login
@flush_cache
@exception_handler
def remove_ieml_script(body):
    script_ast = sc(body['id'])
    terms_db().remove_term(script_ast, recompute_relations=False)


@need_login
@flush_cache
@exception_handler
def update_ieml_script(body):
    """Updates an IEML Term's properties (mainly the tags, and the paradigm). If the IEML is changed,
    a new term is created"""
    script_ast = sc(body["ID"]) # the ID is used to fireu
    if body["IEML"] == body["ID"]:
        terms_db().update_term(script_ast,
                             tags={ "FR" : body["FR"], "EN" : body["EN"]},
                             root=body["PARADIGM"] == "1", recompute_relations=False)
    else:
        terms_db().remove_term(script_ast)
        terms_db().add_term(sc(body["IEML"]),  # the ieml script's ast
                          {"FR": body["FR"], "EN": body["EN"]},  # the
                          root=body["PARADIGM"] == "1", recompute_relations=False)


def ieml_term_exists(ieml_term):
    """Tries to dig a term from the database"""
    found_term = terms_db().get_term(ieml_term)
    return [found_term] if found_term is not None else []


def en_tag_exists(tag_en):
    return list(terms_db().search_by_tag(tag_en, "EN"))


def fr_tag_exists(tag_fr):
    return list(terms_db().search_by_tag(tag_fr, "FR"))
