import csv
import hashlib

from collections import defaultdict

from bidict._bidict import bidict

from ieml.dictionary.relations import INVERSE_RELATIONS

from ieml.constants import GRAMMATICAL_CLASS_NAMES

from ieml.dictionary import Dictionary, term as _term

MAX_TERMS_DICTIONARY = 19999
_drupal_utils = None


def ieml_term_model(term):
    term = _term(term)

    return {
        'CLASS': GRAMMATICAL_CLASS_NAMES[term.grammatical_class],
        'EN': term.translations.en,
        'FR': term.translations.fr,
        'IEML': str(term.script),
        'LAYER': term.script.layer,
        'PARADIGM': term.script.paradigm,
        'ROOT_PARADIGM': term.root == term,
        'SIZE': term.script.cardinal,
        'INDEX': term.index,
        'RANK': term.rank
    }


def _get_drupal_utils():
    global _drupal_utils
    if _drupal_utils is None:
        _drupal_utils = {
            'drupal_dico': [ieml_term_model(t) for t in Dictionary()]
        }
        _drupal_utils['all_uuid'] = bidict({
                d['IEML']: 1000 + int(hashlib.sha1(d['IEML'].encode()).hexdigest(), 16) % MAX_TERMS_DICTIONARY for d in _drupal_utils['drupal_dico']
        })

    return _drupal_utils

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

    root = _term("O:M:.O:M:.-+M:O:.M:O:.-")

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

        if t0 != t1:
            relations[(t0, t1)].add(relname)

    REL = list(_RELATIONS)

    for i, t0 in enumerate(paradigm):
        for t1 in paradigm[i:]:
            for r in t0.relations.to(t1, relations_types=REL):
                add_rel(t0, t1, r)

    res = []

    for t0, t1 in relations:
        for rel_cat in relations[(t0, t1)]:
            comment = ''
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

    if number:
        return res[:number]
    else:
        return res


with open("../data/relations.csv", 'w') as fp:
    fieldnames = ['commentary', 'relation_name', 'relation_type', 'term_dest', 'term_src']
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for r in tqdm(drupal_relations_dump(all=True)):
        writer.writerow(r)


