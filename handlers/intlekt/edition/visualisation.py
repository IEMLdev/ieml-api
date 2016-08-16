from handlers import usl as _usl
from handlers.commons import exception_handler
from ieml.AST.terms import Term
from models.terms.terms import TermsConnector


@exception_handler
def usl_to_json(usl, language='EN'):
    u = _usl(usl)
    def _walk(u):
        if isinstance(u, Term):
            return {
                'type': u.__class__.__name__.lower(),
                'script': str(u.script),
                'title': TermsConnector().get_term(u.script)['TAGS'][language]
            }
        if len(u.children) == 1:
            return _walk(u.children[0])

        return {
            'type': u.__class__.__name__.lower(),
            'children': [
                _walk(c) for c in u
            ]
        }
    return _walk(u)