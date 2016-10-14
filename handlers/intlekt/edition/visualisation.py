from handlers import usl as _usl
from handlers.commons import exception_handler
from ieml.ieml_objects import Term, Sentence, SuperSentence
from models.terms.terms import TermsConnector

word = "{/[([A:O:.wu.-]+[O:U:.wu.-])*([M:O:.f.-]+[M:M:.o.-M:M:.o.-s.u.-'])]/}";
sentence = "{/[([([k.a.-n.a.-']+[m.o.-m.o.-']+[f.u.-l.u.-d.u.-'])*([n.e.-t.a.-wa.e.-']+[n.i.-k.i.-'])]*[([O:U:.t.-]+[O:A:.t.-])*([e.U:.-]+[s.i.-s.i.-'])]*[([d.S:O:.-])])+([([O:U:.t.-]+[O:A:.t.-])*([e.U:.-]+[s.i.-s.i.-'])]*[([wu.]+[wu.j.-])]*[([T:.-U:.-'S:.-wa.e.-'t.x.-s.y.-',]+[T:.-U:.-'B:.-wa.e.-'t.x.-s.y.-',]+[T:.-A:.-'S:.-wa.e.-'t.x.-s.y.-',])])+([([O:U:.t.-]+[O:A:.t.-])*([e.U:.-]+[s.i.-s.i.-'])]*[([O:S:.e.-]+[O:B:.e.-])*([n.-o.-s.y.-']+[n.-e.-s.y.-']+[n.-u.-s.y.-'])]*[([e.e.-]+[m.u.-f.u.-'])])+([([O:U:.t.-]+[O:A:.t.-])*([e.U:.-]+[s.i.-s.i.-'])]*[([M:M:.a.-b.a.-f.o.-'])]*[([M:S:.wa.-])*([we.]+[E:S:.l.-]+[b.a.-n.a.-'])])+([([wu.]+[wu.j.-])]*[([b.wu.-]+[k.i.-b.i.-t.u.-']+[d.i.-l.i.-'])*([a.a.-]+[m.i.-l.i.-'])]*[([b.e.-b.u.-']+[t.-B:.A:.-']+[n.e.-d.a.-wa.e.-'])*([E:B:.B:M:.-])])+([([b.wu.-]+[k.i.-b.i.-t.u.-']+[d.i.-l.i.-'])*([a.a.-]+[m.i.-l.i.-'])]*[([wa.d.-]+[O:O:.A:.-]+[d.i.-d.i.-'])*([E:B:.wa.-]+[wu.wu.-]+[b.o.-f.o.-'])]*[([E:T:.t.-])])+([([b.wu.-]+[k.i.-b.i.-t.u.-']+[d.i.-l.i.-'])*([a.a.-]+[m.i.-l.i.-'])]*[([U:M:.p.-]+[A:M:.p.-])]*[([we.h.-])*([y.B:.-]+[M:M:.u.-]+[f.a.-d.a.-'])])+([([wa.d.-]+[O:O:.A:.-]+[d.i.-d.i.-'])*([E:B:.wa.-]+[wu.wu.-]+[b.o.-f.o.-'])]*[([e.i.-]+[s.u.-d.u.-d.u.-'])]*[([o.U:.-]+[m.o.-n.o.-']+[n.u.-t.u.-'])])+([([wa.d.-]+[O:O:.A:.-]+[d.i.-d.i.-'])*([E:B:.wa.-]+[wu.wu.-]+[b.o.-f.o.-'])]*[([s.-g.-']+[b.-g.-'])*([s.u.-b.u.-d.u.-'])]*[([E:S:.i.-]+[E:B:.s.-]+[y.a.-])*([m.u.-s.u.-d.u.-'])])+([([s.-g.-']+[b.-g.-'])*([s.u.-b.u.-d.u.-'])]*[([wa.O:O:.-]+[wu.O:O:.-]+[k.e.-l.a.-'])]*[([m.-g.-s.y.-']+[n.-g.-s.y.-']+[d.-g.-s.y.-'])])+([([s.-g.-']+[b.-g.-'])*([s.u.-b.u.-d.u.-'])]*[([b.-i.-s.y.-'])*([d.T:O:.-]+[d.M:U:.-]+[d.M:A:.-])]*[([n.p.-]+[n.i.-k.i.-'])])+([([s.-g.-']+[b.-g.-'])*([s.u.-b.u.-d.u.-'])]*[([t.o.-m.o.-s.u.-']+[f.a.-s.a.-'])]*[([O:T:.]+[f.O:O:.-])])+([([s.-g.-']+[b.-g.-'])*([s.u.-b.u.-d.u.-'])]*[([n.u.-s.u.-d.u.-']+[e.-O:M:.-we.h.-'])]*[([we.T:.-]+[i.d.-]+[n.e.-s.a.-wa.e.-'])*([E:M:.h.-]+[d.e.-f.i.-'])])+([([t.o.-m.o.-s.u.-']+[f.a.-s.a.-'])]*[([wa.x.-]+[k.wo.-])]*[([T:.-'M:.-'n.-T:.A:.-',]+[M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_])*([E:U:.t.-]+[n.i.-m.i.-t.u.-'])])]/}";


def sample_usls(n, language='EN'):
    return [
        {"ieml" : word, "title" : "Exemple de mot: concept abstrait"},
        {"ieml" : sentence, "title" : "Exemple de phrase: tribunal amour ridé"}
    ]

def recent_usls(n, language='EN'):
    return []

def usl_to_json(usl, language='EN'):
    u = _usl(usl["usl"])
    def _walk(u, start=True):
        if isinstance(u, Term):
            return {
                'type': u.__class__.__name__.lower(),
                'script': str(u.script),
                'singular_sequences': [str(s) for s in u.script.singular_sequences],
                'title': TermsConnector().get_term(u.script)['TAGS'][language]
            }
        if start and len(u.children) == 1:
            return _walk(u.children[0])

        def _build_tree(transition, children_tree, supersentence=False):
            result = {
                'type': 'supersentence-node' if supersentence else 'sentence-node',
                'mode': _walk(transition[2], start=False),
                'node': _walk(transition[1], start=False),
                'children': []
            }
            if transition[1] in children_tree:
                result['children'] = [_build_tree(c, children_tree, supersentence=supersentence) for c in children_tree[transition[1]]]
            return result

        if isinstance(u, Sentence):
            result = {
                'type': 'sentence-root-node',
                'node': _walk(u.graph.root_node, start=False),
                'children': [
                    _build_tree(c, u.graph.parent_nodes) for c in u.graph.parent_nodes[u.graph.root_node]
                ]
            }
        elif isinstance(u, SuperSentence):
            result = {
                'type': 'supersentence-root-node',
                'node': _walk(u.graph.root_node, start=False),
                'children': [
                    _build_tree(c, u.graph.parent_nodes, supersentence=True) for c in u.graph.parent_nodes[u.graph.root_node]
                    ]
            }
        else:
            result = {
                'type': u.__class__.__name__.lower(),
                'children': [_walk(c, start=False) for c in u]
            }

        return result

    return _walk(u)
