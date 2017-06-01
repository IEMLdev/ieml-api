import hashlib
import random
import string
from ieml.ieml_objects.dictionary import Dictionary, save_dictionary, DICTIONARY_FOLDER, load_dictionary

from handlers.commons import exception_handler, ieml_term_model
from ieml.ieml_objects.tools import term
from ieml.script.operator import sc, script

from ..caching import cached, flush_cache
from handlers.dictionary.commons import relation_name_table
from ieml.exceptions import CannotParse
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from ieml.script import MultiplicativeScript, NullScript
from ieml.script.tools import old_canonical, factorize
from .client import need_login


def _build_old_model_from_term_entry(t):

    return {
        "_id": str(t.script),
        "IEML": str(t.script),
        "CLASS": t.grammatical_class,
        "EN": t.translation['en'],
        "FR": t.translation['fr'],
        "PARADIGM": "1" if t.script.paradigm else "0",
        "LAYER": t.script.layer,
        "TAILLE": t.script.cardinal,
        "CANONICAL": old_canonical(t.script),
        "ROOT_PARADIGM": t.root == t,
        "RANK": t.rank
    }


@cached("dictionary_dump", 1000)
@exception_handler
def dictionary_dump():
    return {'success': True,
            'terms': sorted((ieml_term_model(t) for t in Dictionary()), key=lambda c: c['INDEX'])}

MAX_TERMS_DICTIONARY = 50000
Drupal_dico = [ieml_term_model(t) for t in Dictionary()][:30]
all_uuid = {
    d['IEML']: 1000 + int(hashlib.sha1(d['IEML'].encode()).hexdigest(), 16) % MAX_TERMS_DICTIONARY for d in
    Drupal_dico
}

# @cached("dictionary_dump", 1000)
@exception_handler
def drupal_dictionary_dump():
    return [{
                'id': all_uuid[d['IEML']],
                'IEML': d['IEML'],
                'FR': d['FR'],
                'EN': d['EN'],
                'INDEX': d['INDEX']
            } for d in Drupal_dico]

RELATIONS = {
    'Inclusion': [("Contained", "Contains")],
    'Etymology': [("Father in substance", "Child in substance"), ("Father in attribute", "Child in attribute"), ("Father in mode", "Child in mode")],
    'Siblings': [("Opposed", "Opposed"), ("Crossed", "Crossed"), ("Associated", "Associated"), ("Twin", "Twin")]
}

# @cached("dictionary_dump", 1000)
# @exception_handler
# def drupal_dictionary_dump():
#     dico = [ieml_term_model(t) for t in Dictionary()][:5]
#     return _drupal_process(dico)

def drupal_relations_dump():
    res = []
    for rel_cat in RELATIONS:
        for sym in RELATIONS[rel_cat]:
            comment = ''.join([random.choice(string.ascii_lowercase) for i in range(100)])
            term0 = random.choice(Drupal_dico)
            term1 = random.choice(Drupal_dico)

            print(term1)
            res.append({
                'term_src': all_uuid[term0['IEML']],
                'term_dest': all_uuid[term1['IEML']],
                'relation_name': sym[0],
                'relation_type': rel_cat,
                'commentary': comment
            })

            res.append({
                'term_src': all_uuid[term1['IEML']],
                'term_dest': all_uuid[term0['IEML']],
                'relation_name': sym[1],
                'relation_type': rel_cat,
                'commentary': comment
            })

    return res

@cached("all_ieml", 1000)
# @exception_handlerexception_handler
def all_ieml():
    """Returns a dump of all the terms contained in the DB, formatted for the JS client"""
    result = [{**_build_old_model_from_term_entry(t),
              'INDEX': i} for i, t in enumerate(Dictionary())]
    return result


@exception_handler
def get_term(script):
    return _build_old_model_from_term_entry(term(script))

@exception_handler
def parse_ieml(iemltext):
    script_ast = sc(iemltext)
    root = Dictionary().get_root(script_ast)
    containsSize = len([s for s in Dictionary().layers[script_ast.layer] if s.script in script_ast])

    return {
        "factorization": str(factorize(script_ast)),
        "success" : True,
        "level" : script_ast.layer,
        "taille" : script_ast.cardinal,
        "class" : script_ast.script_class,
        "canonical" : old_canonical(script_ast),
        "rootIntersections" : [str(root.script)] if root is not None else [],
        "containsSize": containsSize
    }


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

    def _slice_array(tab, dim):
        shape = tab.cells.shape
        if dim == 1:
            result = [
                _table_entry(1, ieml=tab.paradigm, header=True, top_header=True)
            ]
            result.extend([_table_entry(ieml=e) for e in tab.paradigm.singular_sequences])
        else:
            result = [
                _table_entry(shape[1] + 1, ieml=tab.paradigm, header=True, top_header=True),
                _table_entry(top_header=True)  # grey square
            ]

            for col in tab.columns:
                result.append(_table_entry(ieml=col, header=True))

            for i, line in enumerate(tab.cells):
                result.append(_table_entry(ieml=tab.rows[i], header=True))
                for cell in line:
                    result.append(_table_entry(ieml=cell))

        return result

    def _build_tables(tables):
        result = []
        for table in tables:
            tabs = []

            for i, tab in enumerate(table.headers):
                tabs.append({
                    'tabTitle': str(tab),
                    'slice': _slice_array(table.headers[tab], dim=table.dim)
                })

            result.append({
                'Col': len(table.headers[tab].columns) + 1 if table.dim != 1 else 1,
                'table': tabs
            })

        return result

    try:
        s = sc(iemltext)
        tables = s.tables

        if tables is None:
            return {
                'exception': 'not enough variables to generate table',
                'at': 7,
                'success': False
            }
        return {
            'tree': {
                'input': str(s),
                'Tables': _build_tables(tables)
            },
            'success': True
        }
    except CannotParse:
        pass


@exception_handler
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

    script = sc(iemltext)
    return {
        'level': script.layer,
        'tree': _tree_entry(script),
        'taille': script.cardinal,
        'success': True,
        'canonical': old_canonical(script)
    }


def _process_inhibits(body):
    if 'INHIBITS' in body:
        try:
            inhibits = [relation_name_table[i] for i in body['INHIBITS']]
        except KeyError as e:
            raise ValueError(e.args[0])
    else:
        inhibits = []

    return inhibits


def _save_dictionary():
    try:
        Dictionary().compute_relations()
        Dictionary().compute_ranks()
        save_dictionary(DICTIONARY_FOLDER)
    except ValueError as e:
        load_dictionary(DICTIONARY_FOLDER, Dictionary())
        raise ValueError("Unable to recompute the relations and ranks: " + str(e))


@need_login
@flush_cache
# @exception_handler
def new_ieml_script(body):
    script_ast = sc(body["IEML"])
    Dictionary().add_term(script_ast,
                          root=body["PARADIGM"] == "1",
                          inhibitions=_process_inhibits(body),
                          translation={"fr": body["FR"], "en": body["EN"]})

    if body["PARADIGM"] == "1":
        for i, ss in enumerate(script_ast.singular_sequences):
            Dictionary().add_term(ss,
                                  translation={"fr": body["FR"] + " SS (%d)"%i,
                                               "en": body["EN"] + " SS (%d)"%i})

    for j, table in enumerate(script_ast.tables):
        for i, tab in enumerate(table.headers):
            Dictionary().add_term(tab,
                                  translation={"fr": body["FR"] + " Table (%d) Tab (%d)" % (j,i),
                                               "en": body["EN"] + " Table (%d) Tab (%d)" % (j,i)})

    _save_dictionary()
    return {"success" : True, "added": _build_old_model_from_term_entry(term(script_ast))}


@need_login
@flush_cache
@exception_handler
def remove_ieml_script(body):
    script_ast = sc(body['id'])
    Dictionary().remove_term(term(script_ast))
    _save_dictionary()

    return {'success': True}


@need_login
@flush_cache
@exception_handler
def update_ieml_script(body):
    """Updates an IEML Term's properties (mainly the tags, and the paradigm). If the IEML is changed,
    a new term is created"""
    script_ast = sc(body["ID"])

    inhibits = _process_inhibits(body)

    if body["IEML"] == body["ID"]:
        # no update on the ieml
        Dictionary().update_term(term(script_ast),
                                 inhibitions=inhibits,
                                 translation={"fr": body["FR"], "en": body["EN"]})
    else:
        Dictionary().remove_term(term(script_ast))
        Dictionary().add_term(sc(body["IEML"]),
                              root=body["PARADIGM"] == "1",
                              inhibitions=inhibits,
                              translation={"fr": body["FR"], "en": body["EN"]})
    _save_dictionary()
    return {"success" : True, "modified": _build_old_model_from_term_entry(term(body["IEML"]))}


@exception_handler
def ieml_term_exists(ieml_term):
    """Tries to dig a term from the database"""
    t = script(ieml_term)
    if t in Dictionary():
        return [str(t)]
    else:
        return []


# @exception_handler
def en_tag_exists(tag_en):
    return [tag_en] if tag_en in Dictionary().translations['en'].inv else []


# @exception_handler
def fr_tag_exists(tag_fr):
    return [tag_fr] if tag_fr in Dictionary().translations['fr'].inv else []


def get_terms_ranking(ieml):
    return {'success': True}