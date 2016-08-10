from ieml.operator import sc
from ieml.script.tools import factorize
from models.terms.terms import TermsConnector

tc = TermsConnector()
modif = False
for t in tc.get_all_terms():
    f = str(factorize(sc(t['_id'])))
    if t['_id'] != f:
        modif = True
        tc.terms.remove(t)
        t['_id'] = f
        tc.terms.insert(t)

if modif:
    tc.recompute_relations(all_delete=True)
