from collections import defaultdict
from itertools import chain

import numpy

from ieml.ieml_objects.sentences import SuperSentence, Sentence, Clause, SuperClause
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word, Morpheme
from ieml.paths.parser.parser import PathParser
from ieml.paths.paths import Path, Coordinate, MultiplicativePath, AdditivePath, ContextPath


def path(p):
    if isinstance(p, Path):
        return p
    if isinstance(p, str):
        return PathParser().parse(p)

    try:
        l = list(p)
        if all(isinstance(e, Path) for e in l):
            res = l[0]
            for p in l[1:]:
                res *= p
            return res

    except TypeError:
        pass

    raise ValueError("Invalid argument to create a path.")


def _resolve_path_tree_graph(tree_graph, path):
    if isinstance(path, Coordinate):
        coords = [path]
    else:
        coords = list(path.children)

    result = set()
    c0 = coords[0]
    if c0.kind == 's':
        stack = {tree_graph.root}
    elif c0.kind == 'a':
        # tous les attributs
        stack = {attr[0] for vals in tree_graph.transitions.values() for attr in vals}
    else:
        # tous les modes
        return {attr[1][2] for vals in tree_graph.transitions.values() for attr in vals}

    for c in coords[1:]:
        _stack = set()
        for s in stack:
            if c.kind == 's':
                raise ValueError("Double substance s in path [%s]"%str(path))

            if c.kind == 'm':
                if c.index:
                    _stack.add(tree_graph.transitions[s][c.index][1][2])
                else:
                    _stack |= {vals[1][2] for vals in tree_graph.transitions[s]}

            if c.kind == 'a':
                if c.index:
                    _stack.add(tree_graph.transitions[s][c.index][0])
                else:
                    _stack |= {vals[0] for vals in tree_graph.transitions[s]}

        if not _stack:
            return set()

        stack = _stack

    return stack


def _resolve_path(obj, path):
    """path is a mul of coord or a coord"""
    if obj.__class__ not in path.context.accept:
        return set()

    if isinstance(obj, Text):
        if path.index:
            return {obj.children[path.index]}

        return set(obj.children)

    if isinstance(obj, (Sentence, SuperSentence)):
        return _resolve_path_tree_graph(obj.tree_graph, path)

    if isinstance(obj, Word):
        if path.kind == 'r':
            if path.index:
                return {obj.root[path.index]}
            return set(obj.root.children)
        else:
            if path.index:
                return {obj.flexing[path.index]}
            return set(obj.flexing.children)

    if isinstance(obj, Term):
        raise ValueError("Term not deferencable.")


def resolve(ieml_object, path):
    if ieml_object.__class__ not in path.context.accept:
        raise ValueError("Can't resolve [%s] on %s"%(str(path), str(ieml_object)))

    result = set()
    for d in path.develop():
        if isinstance(d, (Coordinate, MultiplicativePath)):
            result |= _resolve_path(ieml_object, d)
        else:
            # context path
            stack = {ieml_object}
            for c in d.children:
                _stack = set()
                for s in stack:
                    _stack |= _resolve_path(s, c)

                if not _stack:
                    break

                stack = _stack
            else:
                result |= stack

    return result


def _enumerate_paths(ieml_obj, level):
    if isinstance(ieml_obj, level):
        yield [], ieml_obj

    if isinstance(ieml_obj, Text):
        for i, t in enumerate(ieml_obj.children):
            for p, e in _enumerate_paths(t, level=level):
                yield [path('t%d'%i)] + p, e

    if isinstance(ieml_obj, (Sentence, SuperSentence)):
        for node in set(node for clause in ieml_obj for node in clause):
            for p, e in _enumerate_paths(node, level=level):
                yield [_tree_graph_path_of_node(ieml_obj.tree_graph, node)] + p, e

    if isinstance(ieml_obj, Word):
        for i, t in enumerate(ieml_obj.root.children):
            for p, e in _enumerate_paths(t, level=level):
                yield [path('r%d'%i)] + p, e

        for i, t in enumerate(ieml_obj.flexing.children):
            for p, e in _enumerate_paths(t, level=level):
                yield [path('f%d' % i)] + p, e

    raise StopIteration


def _tree_graph_path_of_node(tree_graph, node):
    if node in tree_graph.nodes:
        nodes = [(node, False)]
    else:
        nodes = []

    # can be a mode
    nodes += [(c[0], True) for c_list in tree_graph.transitions.values() for c in c_list if c[1][2] == node]
    if not nodes:
        raise ValueError("Node not in tree graph : %s" % str(node))

    def _build_coord(node, mode=False):
        if node == tree_graph.root:
            return [Coordinate(kind='s')]

        parent = tree_graph.nodes[numpy.where(tree_graph.array[:, tree_graph.nodes_index[node]])[0][0]]

        return _build_coord(parent) + \
               [Coordinate(index=[c[0] for c in tree_graph.transitions[parent]].index(node), kind='m' if mode else 'a')]

    return AdditivePath([MultiplicativePath(_build_coord(node, mode)) for node, mode in nodes])


def enumerate_paths(ieml_obj, level=Term):
    for p, t in _enumerate_paths(ieml_obj, level=level):
        if len(p) == 1:
            yield p[0], t
        else:
            yield ContextPath(p), t


def _build_deps_tree_graph(rules):
    def _node():
        return {
            'resolve': defaultdict(_node),
            'context': [],
            'rules': defaultdict(_node)
        }

    # contain s, a et m (relative path to the root)
    roots = defaultdict(_node)

    s = Coordinate(kind='s')

    for p, e in rules:
        if isinstance(p, ContextPath):
            actual_P = p.children[0]  # multiplicative or coordinate
            ctx_P = path(p.children[1:])
        else:
            actual_P = p
            ctx_P = None

        if isinstance(actual_P, MultiplicativePath):
            actual_P = actual_P.children
        else:
            actual_P = [actual_P]

        # actual_p is the list of coordinate to navigate
        # ctx_p is the rest of the path or None

        current_node = roots

        # replacing s0 -> s
        if actual_P[0].kind == 's' and actual_P[0].index == 0:
            actual_P[0] = s

        for c in actual_P[:-1]:
            if c.index is not None:
                categorie = 'resolve'
            else:
                categorie = 'rules'

            current_node = current_node[str(c)][categorie]

        # the nodes with ctx_P is None will be instanciate
        current_node[str(actual_P[-1])]['context'].append((ctx_P, e))

    result = []

    def _merge_nodes(n0, n1):
        for cat in ('resolve', 'rules'):
            for r in n1[cat]:
                if r in n0[cat]:
                    _merge_nodes(n0[cat][r], n1[cat][r])
                else:
                    n0[cat][r] = n1[cat][r]

        # merge ctx
        n0['context'] += n1['context']

    # apply the rules on the tree starting from s
    def _apply_rule(node, mode=False):
        # we add the globals rules to its own
        _merge_nodes(node['rules']['a'], roots['a'])
        _merge_nodes(node['rules']['m'], roots['m'])

        obj = _resolve_ctx(node['context'])

        if mode:
            return obj

        if not node['resolve']:
            raise ValueError("No node to instanciate.")

        # resolve the children
        max_i = max(n.index for n in node['resolve'])

        _result = {
            'a': [],
            'm': []
        }

        for r in ('a', 'm'):
            indexed = {k.index: k for k in node['resolve'] if k.kind == r}
            rules = [k for k in node['rules'] if k.kind == r]

            if max(indexed) + 1 > len(indexed) + (1 if rules else 0):
                raise ValueError("Not enough rules to instanciate all the %s rules."%r)

            for i in range(max_i + 1):
                if i in indexed:
                    child = indexed[i]
                else:
                    child = _node()

                _merge_nodes(child, node['rules'][r])

                _result[r].append(_apply_rule(child, mode=r == 'm'))

        for a, m in zip(_result['a'], _result['m']):
            result.append((obj, a, m))

        return obj
    # 'context' attribute is now the sub element
    # generating the triplet from the root s

    _apply_rule(roots['s'])

    return reversed(result)


def _build_deps_text(rules):
    indexes = defaultdict(list)
    generals = []

    for p, e in rules:
        if isinstance(p, ContextPath):
            actual_P = p.children[0]  # coordinate
            ctx_P = path(p.children[1:])
        else:
            actual_P = p
            ctx_P = None

        if not isinstance(actual_P, Coordinate):
            raise ValueError("A text must be defined by a single coordinate.")

        if actual_P.index is not None:
            indexes[actual_P.index].append((ctx_P, e))
        else:
            generals.append((ctx_P, e))

    if not indexes:
        return []

    if max(indexes) + 1 - len(indexes) > 1:
        # if there is more than one missing
        raise ValueError("Index missing on text definition.")

    i = 0
    result = []
    while i <= max(indexes):
        ctx_rules = generals[:]
        if i in indexes:
            ctx_rules.extend(indexes[i])

        result.append(_resolve_ctx(ctx_rules))
        i += 1

    return result


def _build_deps_word(rules):
    result = {
        'r': {
            'indexes': defaultdict(list),
            'generals': []
        },
        'f': {
            'indexes': defaultdict(list),
            'generals': []
        }
    }

    for p, e in rules:
        if isinstance(p, ContextPath):
            # should be an error but support it
            actual_P = p.children[0]  # coordinate
            ctx_P = path(p.children[1:])
        else:
            actual_P = p
            ctx_P = None

        if not isinstance(actual_P, Coordinate):
            raise ValueError("A word must be defined by a single coordinate.")

        if actual_P.index is not None:
            result[actual_P.kind]['indexes'][actual_P.index].append((ctx_P, e))
        else:
            result[actual_P.kind]['generals'].append((ctx_P, e))

    for k in result:
        indexes = result[k]['indexes']
        generals = result[k]['generals']

        if not indexes and not generals:
            result[k] = []
            continue

        if max(indexes) + 1 > len(indexes) + len(generals):
            # if there is more than one missing
            raise ValueError("Index missing on word (%s) definition."%k)

        current = []
        length = len(indexes) + len(generals)
        generals = generals.__iter__()
        for i in range(length):
            if i in indexes:
                ctx_rules = indexes[i]
            else:
                ctx_rules = [next(generals)]

            current.append(_resolve_ctx(ctx_rules))

        result[k] = current

    return result


def _inferred_types(path, e):
    result = set()
    for inf in path.context.switch:
        if e.__class__ in path.context.switch[inf]:
            result.add(inf)

    if result:
        return result

    raise ValueError("No compatible type found with the path %s and the ieml object of type %s"%
                     (str(path), e.__class__.__name__))


def _resolve_ctx(rules):

    # if rules == [(None, e)] --> e
    if len(rules) == 1 and rules[0][0] is None:
        return rules[0][1]


    if any(r[0] is None for r in rules):
        raise ValueError("Multiple definition, multiple ieml object provided.")

    if any(not isinstance(r[0], Path) for r in rules):
        raise ValueError("Must have only path instance.")

    r0 = rules[0]
    types = _inferred_types(*r0)
    for r in rules:
        types = types.intersection(_inferred_types(*r))

    if not types:
        raise ValueError("No definition, no type inferred on rules list.")

    if len(types) > 1:
        raise ValueError("Multiple definition, multiple type inferred on rules list.")

    type = next(types.__iter__())

    if type == Word:
        deps = _build_deps_word(rules)
        flexing = None
        if deps['f']:
            flexing = Morpheme(deps['f'])
        return Word(Morpheme(deps['r']), flexing)

    if type == Text:
        deps = _build_deps_text(rules)
        return Text(deps)

    if type in (SuperSentence, Sentence):
        deps = _build_deps_tree_graph(rules)
        if type == Sentence:
            clauses = []
            for s, a, m in deps:
                clauses.append(Clause(a, s, m))
            return Sentence(clauses)
        else:
            clauses = []
            for s, a, m in deps:
                clauses.append(SuperClause(a, s, m))
            return SuperSentence(clauses)

    raise ValueError("Invalid type inferred %s"%type.__name__)


def resolve_ieml_object(paths, elements=None):
    if elements is None:
        return _resolve_ctx(list(paths))
    return _resolve_ctx([(d, e) for e, p in zip(elements, paths) for d in p.develop()])

