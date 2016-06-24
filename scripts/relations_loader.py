import progressbar

from ieml.parsing import ScriptParser
from models.relations import RelationsQueries
from models.relations.relations import RelationsConnector
from models.terms.terms import TermsConnector
from ieml.script.constants import OPPOSED_SIBLING_RELATION, ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, \
    TWIN_SIBLING_RELATION, FATHER_RELATION, SUBSTANCE, ATTRIBUTE, MODE


inhibits_map_to_relation = {
    "Crossed siblings": CROSSED_SIBLING_RELATION,
    "Associated siblings": ASSOCIATED_SIBLING_RELATION,
    "Twin siblings": TWIN_SIBLING_RELATION,
    "Ancestors in mode": FATHER_RELATION + '.' + MODE,
    "Opposed siblings": OPPOSED_SIBLING_RELATION,
    "Ancestors in attribute": FATHER_RELATION + '.' + ATTRIBUTE,
    "Ancestors in substance": FATHER_RELATION + '.' + SUBSTANCE
}


def load_old_db():
    scripts = RelationsConnector()
    terms = TermsConnector()
    parser = ScriptParser()

    terms.terms.remove({})
    scripts.scripts.remove({})

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

    terms.save_multiple_terms(terms_list)
    print('\n\nDone.', flush=True)


def recompute_relations():
    terms = TermsConnector()
    paradigms = terms.root_paradigms()

    computation = progressbar.ProgressBar(max_value=len(paradigms))
    for i, p in enumerate(paradigms):
        computation.update(i + 1)
        RelationsQueries.compute_relations(p['_id'], p['INHIBITS'])

if __name__ == '__main__':
    load_old_db()
