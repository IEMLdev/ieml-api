import hashlib
import random
import string
from collections import defaultdict

from handlers.caching import memoized
from ieml.commons import LANGUAGES
from ieml.ieml_objects.terms import Dictionary, term

from handlers.commons import exception_handler, ieml_term_model
from ieml.ieml_objects.terms.relations import INVERSE_RELATIONS
from ieml.ieml_objects.terms.version import DictionaryVersion, create_dictionary_version, \
    get_available_dictionary_version
from ieml.script.operator import sc, script

from ..caching import flush_cache
from handlers.dictionary.commons import relation_name_table
from ieml.exceptions import CannotParse
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from ieml.script.tools import old_canonical, factorize
from .client import need_login


def _build_old_model_from_term_entry(t):
    return {
        "_id": str(t.script),
        "IEML": str(t.script),
        "CLASS": t.grammatical_class,
        "EN": t.translations['en'],
        "FR": t.translations['fr'],
        "PARADIGM": "1" if t.script.paradigm else "0",
        "LAYER": t.script.layer,
        "TAILLE": t.script.cardinal,
        "CANONICAL": old_canonical(t.script),
        "ROOT_PARADIGM": t.root == t,
        "RANK": t.rank,
        "INDEX": t.index
    }


@exception_handler
def dictionary_dump(dictionary_version=None):
    if dictionary_version is not None:
        version = DictionaryVersion.from_file_name(dictionary_version)
    else:
        version = None

    return {'success': True,
            'terms': sorted((ieml_term_model(t) for t in Dictionary(version)), key=lambda c: c['INDEX'])}

MAX_TERMS_DICTIONARY = 50000
_drupal_utils = None


def _get_drupal_utils():
    global _drupal_utils
    if _drupal_utils is None:
        _drupal_utils = {
            'drupal_dico': [ieml_term_model(t) for t in Dictionary()]
        }
        _drupal_utils['all_uuid'] = {
                d['IEML']: 1000 + int(hashlib.sha1(d['IEML'].encode()).hexdigest(), 16) % MAX_TERMS_DICTIONARY for d in _drupal_utils['drupal_dico']
        }

    return _drupal_utils


# @cached("dictionary_dump", 1000)
@exception_handler
def drupal_dictionary_dump():
    _drupal_utils = _get_drupal_utils()

    return [{
                'id': _drupal_utils['all_uuid'][d['IEML']],
                'IEML': d['IEML'],
                'FR': d['FR'],
                'EN': d['EN'],
                'INDEX': d['INDEX'],
                'CARDINALITY': d['SIZE'],
                'LAYER': d['LAYER'],
                'RANK': d['RANK'],
                'CLASS': d['CLASS'][0] + d['CLASS'][1:].lower(),
                'PARADIGM': d['PARADIGM'],
                'ROOT_PARADIGM': d['ROOT_PARADIGM'],
            } for d in _drupal_utils['drupal_dico']]


_RELATIONS = {'contains': 'inclusion',         # 0
             'contained': 'inclusion',        # 1
             'father_substance': 'etymology', # 2
             'child_substance': 'etymology',  # 3
             'father_attribute': 'etymology', # 4
             'child_attribute': 'etymology',  # 5
             'father_mode': 'etymology',      # 6
             'child_mode': 'etymology',       # 7
             'opposed': 'sibling',          # 8
             'associated': 'sibling',       # 9
             'crossed': 'sibling',          # 10
             'twin': 'sibling'}


def drupal_relations_dump(number=None, all=False):
    _drupal_utils = _get_drupal_utils()

    root = term("O:M:.O:M:.-+M:O:.M:O:.-")

    if all:
        paradigm = list(Dictionary())
    else:
        paradigm = sorted(Dictionary().roots[root])

    relations = defaultdict(set)

    def add_rel(t0, t1, relname):
        if t1 > t0:
            q = t0
            t0 = t1
            t1 = q

        relations[(t0, t1)].add(relname)

    REL = list(_RELATIONS)

    for i, t0 in enumerate(paradigm):
        for t1 in paradigm[i:]:
            for r in t0.relations.to(t1, relations_types=REL):
                add_rel(t0, t1, r)

    res = []

    for t0, t1 in relations:
        for rel_cat in relations[(t0, t1)]:
            comment = ''.join([random.choice(string.ascii_lowercase) for i in range(10)])
            res.append({
                'term_src': _drupal_utils['all_uuid'][str(t0.script)],
                'term_dest': _drupal_utils['all_uuid'][str(t1.script)],
                'relation_name': rel_cat,
                'relation_type': _RELATIONS[rel_cat],
                'commentary': comment
            })

            res.append({
                'term_src': _drupal_utils['all_uuid'][str(t1.script)],
                'term_dest': _drupal_utils['all_uuid'][str(t0.script)],
                'relation_name': INVERSE_RELATIONS[rel_cat],
                'relation_type': _RELATIONS[rel_cat],
                'commentary': comment
            })

        # for sym in RELATIONS[rel_cat]:
        #     comment = ''.join([random.choice(string.ascii_lowercase) for i in range(100)])
        #     term0 = random.choice(Drupal_dico)
        #     term1 = random.choice(Drupal_dico)
        #
        #     print(term1)
    # print(len(res))
    if number:
        return res[:number]
    else:
        return res

@memoized("all_ieml", 1000)
# @exception_handler
def all_ieml(version):
    """Returns a dump of all the terms contained in the DB, formatted for the JS client"""
    result = [_build_old_model_from_term_entry(t) for t in Dictionary(version)]
    return result

@exception_handler
def parse_ieml(iemltext, version):
    script_ast = sc(iemltext)
    root = Dictionary(version).get_root(script_ast)
    containsSize = len([s for s in Dictionary(version).layers[script_ast.layer] if s.script in script_ast])

    return {
        "factorization": str(factorize(script_ast)),
        "success" : True,
        "level" : script_ast.layer,
        "taille" : script_ast.cardinal,
        "class" : script_ast.script_class,
        "rootIntersections" : [str(root.script)] if root is not None else [],
        "containsSize": containsSize
    }


def script_table(ieml):
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
                'table': tabs,
                'dim': table.dim
            })

        return result

    try:
        s = sc(ieml)
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


def _process_inhibits(body):
    if 'INHIBITS' in body:
        try:
            inhibits = [relation_name_table[i] for i in body['INHIBITS']]
        except KeyError as e:
            raise ValueError(e.args[0])
    else:
        inhibits = []

    return inhibits


@need_login
@flush_cache
@exception_handler
def new_ieml_script(body, version):
    script_ast = sc(body["IEML"])
    to_add = {
        'terms': [str(script_ast)],
        'roots': [str(script_ast)] if body["PARADIGM"] == "1" else [],
        'inhibitions': {str(script_ast): _process_inhibits(body)} if body["PARADIGM"] == "1" else {},
        'translations': {"fr": {str(script_ast): body["FR"]},
                         "en": {str(script_ast): body["EN"]}}
    }

    if body["PARADIGM"] == "1":
        for i, ss in enumerate(script_ast.singular_sequences):
            to_add['terms'].append(str(ss))
            to_add['translations']['fr'][str(ss)] = body["FR"] + " SS (%d)"%i
            to_add['translations']['en'][str(ss)] = body["EN"] + " SS (%d)"%i

    for j, table in enumerate(script_ast.tables):
        for i, tab in enumerate(table.tabs):
            if tab.paradigm != script_ast:
                to_add['terms'].append(str(tab.paradigm))
                to_add['translations']['fr'][str(tab.paradigm)] = body["FR"] + " Table (%d) Tab (%d)" % (j,i)
                to_add['translations']['en'][str(tab.paradigm)] = body["EN"] + " Table (%d) Tab (%d)" % (j,i)

    new_version = create_dictionary_version(DictionaryVersion.from_file_name(version), add=to_add)
    new_version.upload_to_s3()

    return {"success" : True, "added": _build_old_model_from_term_entry(term(script_ast, dictionary=new_version))}


@need_login
@flush_cache
@exception_handler
def remove_ieml_script(body, version):
    script_ast = sc(body['id'])
    if script_ast.cardinal == 1:
        raise ValueError("Can't remove %s, it is a singular sequence."%str(script_ast))

    t = term(script_ast, dictionary=Dictionary(version))
    if t.root == t:
        to_remove = [str(tt.script) for tt in t.relations.contains]
    else:
        to_remove = [script_ast]

    new_version = create_dictionary_version(DictionaryVersion(version), remove=to_remove)
    new_version.upload_to_s3()

    return {'success': True}


@need_login
@flush_cache
@exception_handler
def update_ieml_script(body, version):
    """Updates an IEML Term's properties (mainly the tags, and the paradigm). If the IEML is changed,
    a new term is created"""
    script_ast = sc(body["ID"])
    inhibits = _process_inhibits(body)

    if body["IEML"] == body["ID"]:
        # no update on the ieml only update the translations or inhibitions
        to_update = {
            'translations': {"fr": {str(script_ast): body["FR"]},
                             "en": {str(script_ast): body["EN"]}},
        }

        if inhibits:
            to_update['inhibitions'] =  {str(script_ast): inhibits}

        to_remove = None
        to_add = None

    else:
        t = term(script_ast, dictionary=Dictionary(version))
        if script_ast.cardinal == 1 or t.root == t:
            raise ValueError("Can only update the script of a non-root paradigm.")

        to_update = None
        to_remove = [script_ast]

        new_script = script(body["IEML"])
        to_add = {
            'terms': [str(new_script)],
            'translations': {l: {str(new_script): t.translations[l]} for l in LANGUAGES}
        }

    new_version = create_dictionary_version(DictionaryVersion(version), remove=to_remove, add=to_add, update=to_update)
    new_version.upload_to_s3()

    return {"success": True, "modified": _build_old_model_from_term_entry(term(body["IEML"], dictionary=new_version))}


@exception_handler
def ieml_term_exists(ieml_term, version):
    """Tries to dig a term from the database"""
    t = script(ieml_term)
    if t in Dictionary(version):
        return [str(t)]
    else:
        return []


# @exception_handler
def en_tag_exists(tag_en, version):
    return [tag_en] if tag_en in Dictionary(version).translations['en'].inv else []


# @exception_handler
def fr_tag_exists(tag_fr, version):
    return [tag_fr] if tag_fr in Dictionary(version).translations['fr'].inv else []


def get_last_version():
    return str(sorted(get_available_dictionary_version())[-1])

