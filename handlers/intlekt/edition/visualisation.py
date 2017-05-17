from functools import partial

from ieml.ieml_objects.hypertexts import Hyperlink, Hypertext
from ieml.ieml_objects.sentences import Clause, SuperClause
from ieml.ieml_objects.tools import term
from ieml.ieml_objects.words import Word, Morpheme
from ieml.paths.exceptions import IEMLObjectResolutionError
from ieml.usl.tools import usl as _usl, usl
from handlers.commons import exception_handler, ieml_term_model
from ieml.ieml_objects import Term, Sentence, SuperSentence
from ieml.ieml_objects.texts import Text

from models.terms.terms import TermsConnector
from models.usls.library import LibraryConnector

word = "[([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]"
sentence = "[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([S:.-'B:.-'n.-S:.U:.-',])]*[([E:T:.f.-])])+([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([t.i.-s.i.-'u.T:.-U:.-'wo.-',B:.-',_M:.-',_;])]*[([E:E:T:.])])]"
supersentence = "[([([([wo.s.-]+[o.wa.-]+[M:O:.j.-])*([E:A:.wu.-]+[d.i.-m.i.-t.u.-'])]*[([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])]*[([x.t.-]+[e.-o.-we.h.-']+[t.e.-m.u.-'])*([o.h.-]+[n.o.-d.o.-'])])+([([wo.s.-]+[o.wa.-]+[M:O:.j.-])*([E:A:.wu.-]+[d.i.-m.i.-t.u.-'])]*[([e.-o.-we.h.-']+[t.e.-m.u.-']+[n.o.-d.o.-'])*([t.a.-k.a.-']+[d.i.-m.i.-t.u.-'])]*[([S:M:.]+[b.u.-]+[M:O:.j.-])*([b.u.-]+[t.e.-m.u.-'])])]*[([([wo.s.-]+[n.j.-]+[x.t.-])*([b.u.-]+[s.i.-b.i.-t.u.-'])]*[([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([x.t.-]+[e.-o.-we.h.-']+[t.e.-m.u.-'])*([o.h.-]+[n.o.-d.o.-'])])+([([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([S:M:.]+[E:B:.b.-]+[c.b.-])*([wo.s.-]+[c.b.-])]*[([S:M:.]+[E:B:.b.-]+[n.o.-d.o.-'])*([E:B:.b.-]+[o.h.-])])+([([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([E:B:.b.-]+[x.t.-]+[e.-o.-we.h.-'])*([o.wa.-]+[n.j.-])]*[([E:B:.b.-]+[x.t.-]+[e.-o.-we.h.-'])*([o.wa.-]+[n.j.-])])+([([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([wo.s.-]+[o.wa.-]+[M:O:.j.-])*([E:A:.wu.-]+[d.i.-m.i.-t.u.-'])]*[([c.b.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.a.-k.a.-'])])]*[([([S:M:.]+[E:B:.b.-]+[c.b.-])*([wo.s.-]+[c.b.-])]*[([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])]*[([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])])+([([S:M:.]+[E:B:.b.-]+[c.b.-])*([wo.s.-]+[c.b.-])]*[([E:A:.wu.-]+[wo.s.-]+[t.a.-k.a.-'])*([S:M:.]+[e.-o.-we.h.-'])]*[([wo.s.-]+[n.j.-]+[x.t.-])*([s.i.-b.i.-t.u.-']+[t.e.-m.u.-'])])+([([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])]*[([E:A:.wu.-]+[s.i.-b.i.-t.u.-']+[t.o.-d.o.-s.u.-'])*([n.j.-]+[t.i.-s.i.-'])]*[([S:M:.]+[E:A:.wu.-]+[E:B:.b.-])*([e.-o.-we.h.-']+[b.e.-s.u.-'])])])+([([([wo.s.-]+[o.wa.-]+[M:O:.j.-])*([E:A:.wu.-]+[d.i.-m.i.-t.u.-'])]*[([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])]*[([x.t.-]+[e.-o.-we.h.-']+[t.e.-m.u.-'])*([o.h.-]+[n.o.-d.o.-'])])+([([wo.s.-]+[o.wa.-]+[M:O:.j.-])*([E:A:.wu.-]+[d.i.-m.i.-t.u.-'])]*[([e.-o.-we.h.-']+[t.e.-m.u.-']+[n.o.-d.o.-'])*([t.a.-k.a.-']+[d.i.-m.i.-t.u.-'])]*[([S:M:.]+[b.u.-]+[M:O:.j.-])*([b.u.-]+[t.e.-m.u.-'])])]*[([([wo.s.-]+[n.j.-]+[x.t.-])*([s.i.-b.i.-t.u.-']+[t.e.-m.u.-'])]*[([E:A:.wu.-]+[wo.s.-]+[t.a.-k.a.-'])*([S:M:.]+[e.-o.-we.h.-'])]*[([wo.s.-]+[n.j.-]+[x.t.-])*([b.u.-]+[s.i.-b.i.-t.u.-'])])+([([E:A:.wu.-]+[wo.s.-]+[t.a.-k.a.-'])*([S:M:.]+[e.-o.-we.h.-'])]*[([S:M:.]+[b.u.-]+[M:O:.j.-])*([b.u.-]+[t.e.-m.u.-'])]*[([wo.s.-]+[s.i.-b.i.-t.u.-']+[n.o.-d.o.-'])*([E:B:.b.-]+[t.o.-d.o.-s.u.-'])])+([([E:A:.wu.-]+[wo.s.-]+[t.a.-k.a.-'])*([S:M:.]+[e.-o.-we.h.-'])]*[([E:B:.b.-]+[x.t.-]+[e.-o.-we.h.-'])*([o.wa.-]+[n.j.-])]*[([S:M:.]+[n.j.-]+[t.o.-d.o.-s.u.-'])*([S:M:.]+[M:O:.j.-])])]*[([([S:M:.]+[E:B:.b.-]+[n.o.-d.o.-'])*([E:B:.b.-]+[o.h.-])]*[([S:M:.]+[E:B:.b.-]+[c.b.-])*([wo.s.-]+[c.b.-])]*[([b.u.-]+[M:O:.j.-]+[t.e.-m.u.-'])*([t.a.-k.a.-']+[n.o.-d.o.-'])])+([([S:M:.]+[E:B:.b.-]+[n.o.-d.o.-'])*([E:B:.b.-]+[o.h.-])]*[([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([e.-o.-we.h.-']+[t.e.-m.u.-']+[n.o.-d.o.-'])*([t.a.-k.a.-']+[d.i.-m.i.-t.u.-'])])+([([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([c.b.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.a.-k.a.-'])]*[([t.o.-d.o.-s.u.-']+[t.i.-s.i.-']+[d.i.-m.i.-t.u.-'])*([wo.s.-]+[x.t.-])])+([([n.j.-]+[t.e.-m.u.-']+[t.a.-k.a.-'])*([o.h.-]+[t.i.-s.i.-'])]*[([x.t.-]+[e.-o.-we.h.-']+[t.e.-m.u.-'])*([o.h.-]+[n.o.-d.o.-'])]*[([E:B:.b.-]+[x.t.-]+[e.-o.-we.h.-'])*([o.wa.-]+[n.j.-])])])]";

def sample_usls(n, language='EN'):
    return [
        {"ieml" : word, "tags" : { 'FR' : "Nous avons l'intention de fabriquer et de vendre beaucoup",
                                    'EN' : "We intend to make and sell a lot" }, 'keywords': {"FR":[], "EN":[]}},
        {"ieml" : sentence, "tags" : { 'FR': "Nous avons l'intention de fabriquer et de vendre beaucoup de nos véhicules à roues sans conducteurs en Europe",
                                        'EN': "We intend to make and sell a lot of driverless vehicles in Europe"}, 'keywords': {"FR":[], "EN":[]}},
        {"ieml" : supersentence, "tags" : { 'FR': "Superphrase générée aléatoirement",
                                             'EN': "Randomly generated supersentence"}, 'keywords': {"FR":[], "EN":[]}}
    ]


def recent_usls(n, language='EN'):
    return [{'success': True,
             'id': usl['_id'],
             'ieml': usl['USL']['IEML'],
             'tags': usl['TRANSLATIONS'],
             'keywords': usl['KEYWORDS']
            } for usl in LibraryConnector().most_recent(int(n))]


def _ieml_object_to_json(u, start=True):
    if isinstance(u, Term):
        return {"term": ieml_term_model(u),
                "type": "term"}

    if not u.closable and start and len(u.children) == 1:
        return _ieml_object_to_json(u.children[0])

    def _build_tree(transition, children_tree, supersentence=False):
        result = {
            'type': 'supersentence-node' if supersentence else 'sentence-node',
            'mode': _ieml_object_to_json(transition[1].mode, start=False),
            'node': _ieml_object_to_json(transition[0], start=False),
            'children': []
        }
        if transition[0] in children_tree:
            result['children'] = [_build_tree(c, children_tree, supersentence=supersentence) for c in
                                  children_tree[transition[0]]]
        return result

    if isinstance(u, Sentence):
        result = {
            'type': 'sentence-root-node',
            'node': _ieml_object_to_json(u.tree_graph.root, start=False),
            'children': [
                _build_tree(c, u.tree_graph.transitions) for c in u.tree_graph.transitions[u.tree_graph.root]
                ]
        }
    elif isinstance(u, SuperSentence):
        result = {
            'type': 'supersentence-root-node',
            'node': _ieml_object_to_json(u.tree_graph.root, start=False),
            'children': [
                _build_tree(c, u.tree_graph.transitions, supersentence=True) for c in
                u.tree_graph.transitions[u.tree_graph.root]
                ]
        }
    else:
        result = {
            'type': u.__class__.__name__.lower(),
            'children': [_ieml_object_to_json(c, start=False) for c in u]
        }

    return result


@exception_handler
def usl_to_json(usl):
    u = _usl(usl["usl"])
    return _ieml_object_to_json(u.ieml_object)


# @exception_handler
def ieml_to_json(body):
    u = _usl(body['ieml'])
    return {'success': True,
            'json': _ieml_object_to_json(u.ieml_object)}


def _tree_node(json, constructor):
    result = []
    for child in json['children']:
        result.append(
            constructor(substance=_json_to_ieml(json['node']),
                        attribute=_json_to_ieml(child['node']),
                        mode=_json_to_ieml(child['mode'])))
        result.extend(_tree_node(child, constructor))
    return result


def _children_list(constructor, json):
    return constructor(children=list(_json_to_ieml(c) for c in json['children']))

type_to_action = {
    Term.__name__.lower(): lambda json: term(json['term']['IEML']),
    'sentence-root-node': lambda json: Sentence(_tree_node(json, Clause)),
    'supersentence-root-node': lambda json: SuperSentence(_tree_node(json, SuperClause)),
    'sentence-node': lambda json: Sentence(_tree_node(json, Clause)),
    'supersentence-node': lambda json: SuperSentence(_tree_node(json, SuperClause)),
}
for cls in (Morpheme, Word, Text, Hyperlink, Hypertext):
    type_to_action[cls.__name__.lower()] = partial(_children_list, cls)


def _json_to_ieml(json):
    try:
        return type_to_action[json['type']](json)
    except KeyError as k:
        raise ValueError("The node of type %s was unexpected. Invalid json structure."%str(k))


@exception_handler
def json_to_usl(json):
    """Convert a json representation of an usl to the usl object and return the ieml string."""
    return str(usl(_json_to_ieml(json['json'])))


def _path_to_usl_clean(rules):
    try:
        return True, usl(rules)
    except IEMLObjectResolutionError as e:
        return False, {
            'success': False,
            'errors': [{
                'path': p,
                'message': m
            } for p, m in e.errors]
        }


@exception_handler
def rules_to_usl(rules):
    success, result = _path_to_usl_clean([(r[0], term(r[1])) for r in rules])
    if success:
        return str(result)
    return result


@exception_handler
def rules_to_json(rules):
    success, u = _path_to_usl_clean([(r[0], term(r[1])) for r in rules])
    if not success:
        return u
    return _ieml_object_to_json(u.ieml_object)



def usl_to_rules(body):
    u = usl(body['ieml'])
    return {'success': True,
            'rules': [{'path': str(p),
                       'ieml': str(t.script)} for ps, t in u.paths.items() for p in ps.develop]}


def to_ieml(body):
    if 'rules' in body and isinstance(body['rules'], list):
        success, result = _path_to_usl_clean([(r['path'], Term(r['ieml'])) for r in body['rules']])
        if success:
            response = {'success': True,
                    'ieml': str(result)}
        else:
            return result

    elif 'json' in body and isinstance(body['json'], dict):
        response = {'success': True,
                  'ieml': str(_json_to_ieml(body['json']))}

    else:
        raise ValueError("No representation to convert in ieml. Specify at least one of the 'rules' "
                         "or the 'json' body attributes.")

    u = LibraryConnector().get(usl=response['ieml'])
    if u is None:
        response['defined'] = False
        response['translations'] = usl(response['ieml']).auto_translation()
    else:
        response['defined'] = True
        response['translations'] = u['TRANSLATIONS']

    return response

