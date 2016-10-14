from handlers import usl as _usl
from handlers.commons import exception_handler
from ieml.ieml_objects import Term, Sentence, SuperSentence
from models.terms.terms import TermsConnector


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
