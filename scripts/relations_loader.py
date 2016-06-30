#!/usr/bin/env python3
import progressbar
import pprint
from ieml.parsing import ScriptParser
from models.relations import RelationsQueries
from models.relations.relations import RelationsConnector
from models.terms.terms import TermsConnector
from ieml.script.constants import OPPOSED_SIBLING_RELATION, ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, \
    TWIN_SIBLING_RELATION, FATHER_RELATION, SUBSTANCE, ATTRIBUTE, MODE, CHILD_RELATION, CONTAINED_RELATION, \
    CONTAINS_RELATION,ELEMENTS
from bidict import bidict


inhibits_map_to_relation = bidict({
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


def load_old_db():
    scripts = RelationsConnector()
    terms = TermsConnector()
    parser = ScriptParser()

    terms.terms.remove({})
    scripts.relations.remove({})

    relations_inhibits = (scripts.old_db['relviz'].find({}))
    inhibits = {}
    for r in relations_inhibits:
        inhibits[r['id']] = [inhibits_map_to_relation[k] for k in r['viz']]

    terms_list = [{
                'AST': parser.parse(t['IEML']),
                'ROOT': t['PARADIGM'] == '1',
                'TAGS': {
                    'FR': t['FR'],
                    'EN': t['EN']
                },
                'INHIBITS': inhibits[t['IEML']] if t['IEML'] in inhibits else [],
                'METADATA': {}
             } for t in scripts.old_terms.find({})]
    if len(terms_list) != 0:
        terms.save_multiple_terms(terms_list)
    print('\n\nDone.', flush=True)


def recompute_relations():
    terms = TermsConnector()
    paradigms = terms.root_paradigms()

    computation = progressbar.ProgressBar(max_value=len(paradigms))
    for i, p in enumerate(paradigms):
        computation.update(i + 1)
        RelationsQueries.compute_relations(p['_id'])

    RelationsQueries.compute_global_relations()
    RelationsQueries.do_inhibition(TermsConnector().get_inhibitions())

def check_old_relations():
    terms = TermsConnector()
    db_rel = RelationsConnector()

    # document by [ieml -> [relation_type -> [ieml]]]
    relations = terms.old_db['relationships'].aggregate([
        {'$match': {'exists': True}},
        {'$group': {'_id': {'s': '$start', 'type': '$type'}, 'ends': {'$push': '$ieml'}}},
        {'$group': {'_id': '$_id.s', 'relations': {'$push': {'type': '$_id.type', 'ends': '$ends'}}}}
    ])

    errors = {}

    def error(src, r, dest, more):
        if r['type'] not in errors:
            errors[r['type']] = {}
        # if src['_id'] not in errors[r['type']]:
        #     errors[r['type']][src['_id']] = []

        errors[r['type']][('<' if more else '>') + src['_id']] = dest

    def walk_dict(d, k):
        for e in k.split('.'):
            if e not in d:
                return []
            d = d.__getitem__(e)

        if isinstance(d, dict):
            if ELEMENTS in d:
                result = d[ELEMENTS]
                result.extend(walk_dict(d, ATTRIBUTE))
                result.extend(walk_dict(d, SUBSTANCE))
                result.extend(walk_dict(d, MODE))
                return result
            else:
                return []
        return d

    # check the inclusion of old relation in new db
    bar = progressbar.ProgressBar()
    for src in bar(relations):
        script = db_rel.get_script(src['_id'])

        if script is None:
            print('error on %s'%str(src['_id']))
            continue

        script_relations = RelationsQueries.relations(script['_id'], pack_ancestor=True)
        for r in src['relations']:
            if r['type'] == 'Belongs to Paradigm':
                if r['ends'][0] != script['ROOT']:
                    error(src, r, r['ends'][0], more=True)
                continue

            type = inhibits_map_to_relation[r['type']]
            if type not in script_relations:
                error(src, r, r['ends'], more=True)
                continue

            more = set(r['ends']).difference(script_relations[type])
            if more:
                error(src, r, more, more=True)
            less = set(script_relations[type]).difference(r['ends'])
            if less:
                error(src, r, less, more=False)

    with open('diff.txt', 'w') as f:
        pprint.pprint(errors, f)

if __name__ == '__main__':
    load_old_db()
    # RelationsQueries.compute_global_relations()
    # RelationsQueries.do_inhibition(TermsConnector().get_inhibitions())
    # recompute_relations()
    check_old_relations()
