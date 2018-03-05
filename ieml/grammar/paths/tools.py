from collections import defaultdict

import numpy

from ieml.exceptions import InvalidPathException
from ieml.grammar import topic, text, fact, theory
from ieml.tools import ieml
from ...exceptions import InvalidIEMLObjectArgument
from ...grammar import Theory, Fact, Text, Word, Topic
from ...exceptions import IEMLObjectResolutionError, ResolveError
from .parser import PathParser
from .paths import Path, Coordinate, MultiplicativePath, AdditivePath, ContextPath


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
                raise InvalidPathException(tree_graph, path, "double substance 's' (root node).")

            if c.kind == 'm':
                if c.index is not None:
                    _stack.add(tree_graph.transitions[s][c.index][1][2])
                else:
                    _stack |= {vals[1][2] for vals in tree_graph.transitions[s]}

            if c.kind == 'a':
                if c.index is not None:
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
        result = set()
        for ctx in path.context.accept:
            result |= {e for u in obj[ctx] for e in _resolve_path(u, path)}

        return result

    if isinstance(obj, Text):
        if path.index is not None:
            return {obj.children[path.index]}

        return set(obj.children)

    if isinstance(obj, (Fact, Theory)):
        return _resolve_path_tree_graph(obj.tree_graph, path)

    if isinstance(obj, Topic):
        if path.kind == 'r':
            if path.index is not None:
                return {obj.root[path.index]}
            return set(obj.root)
        else:
            if path.index is not None:
                return {obj.flexing[path.index]}
            return set(obj.flexing)


def resolve(usl, path):
    """"""

    # if usl.__class__ not in path.context.accept:
    #     raise InvalidPathException(usl, path, "invalid path context, expected types: {%s}."%', '.join(path.context.accept))

    result = set()
    for d in path.develop:
        if isinstance(d, (Coordinate, MultiplicativePath)):
            result |= _resolve_path(usl, d)
        else:
            # context path
            stack = {usl}
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


def _enumerate_paths(usl, level):
    if isinstance(usl, level):
        yield [], usl

    if isinstance(usl, Text):
        for i, t in enumerate(usl.children):
            for p, e in _enumerate_paths(t, level=level):
                yield [path('t%d'%i)] + p, e

    if isinstance(usl, (Theory)):
        for node in usl.facts:
            for p, e in _enumerate_paths(node, level=level):
                yield [_tree_graph_path_of_node(usl.tree_graph, node)] + p, e

    if isinstance(usl, (Fact)):
        for node in usl.topics:
            for p, e in _enumerate_paths(node, level=level):
                yield [_tree_graph_path_of_node(usl.tree_graph, node)] + p, e

    if isinstance(usl, Topic):
        for i, t in enumerate(usl.root):
            for p, e in _enumerate_paths(t, level=level):
                yield [path('r%d'%i)] + p, e

        if usl.flexing:
            for i, t in enumerate(usl.flexing):
                for p, e in _enumerate_paths(t, level=level):
                    yield [path('f%d' % i)] + p, e

    return


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


def enumerate_paths(ieml_obj, level=Word):
    for p, t in _enumerate_paths(ieml_obj, level=level):
        if len(p) == 1:
            yield p[0], t
        elif not p:
            yield None, t
        else:
            yield ContextPath(p), t


def _build_deps_tree_graph(rules):
    def _node():
        return {
            'resolve': defaultdict(_node),  # the indexed coordinate
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
            actual_P = list(actual_P.children)
        else:
            actual_P = [actual_P]

        # actual_p is the list of coordinate to navigate
        # ctx_p is the rest of the path or None

        current_node = roots

        # replacing s0 -> s
        if actual_P[0].kind == 's' and actual_P[0].index == 0:
            actual_P[0] = s

        first = True
        for c in actual_P:
            if c.index is not None:
                categorie = 'resolve'
            else:
                categorie = 'rules'

            if first:
                current_node = current_node[c]
                first = False
            else:
                current_node = current_node[categorie][c]

        # the nodes with ctx_P is None will be instanciate
        current_node['context'].append((ctx_P, e))

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

    coord_a = Coordinate('a')
    coord_m = Coordinate('m')

    # apply the rules on the tree starting from s
    def _apply_rule(node, _path, mode=False):
        # we add the globals rules to its own
        _merge_nodes(node['rules'][coord_a], roots[coord_a])
        _merge_nodes(node['rules'][coord_m], roots[coord_m])

        obj = _resolve_ctx(_path, node['context'])
        error = obj is None

        if mode or not node['resolve']:
            return error, obj

        # resolve the children
        max_i = max(n.index for n in node['resolve'])

        _result = {
            'a': [],
            'm': []
        }

        for r in ('a', 'm'):
            indexed = {k.index: node['resolve'][k] for k in node['resolve'] if k.kind == r}
            rules = [k for k in node['rules'] if k.kind == r]

            if max(indexed, default=-1) + 1 > len(indexed) + (1 if rules else 0):
                raise ResolveError("Not enough information to instantiate all the %s rules. At %s."%(r, _path))

            for i in range(max_i + 1):
                if i in indexed:
                    child = indexed[i]
                else:
                    child = _node()

                _merge_nodes(child, node['rules'][r])

                e, n = _apply_rule(child, _path + "%s%d"%(r, i), mode=r == 'm')
                error |= e
                _result[r].append(n)

        for a, m in zip(_result['a'], _result['m']):
            result.append((obj, a, m))

        return error, obj
    # 'context' attribute is now the sub element
    # generating the triplet from the root s

    error, o = _apply_rule(roots[s], 's0')

    return error, result[::-1]


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
            raise ResolveError("A text must be defined by a coordinate, not %s"%actual_P)

        if actual_P.index is not None:
            indexes[actual_P.index].append((ctx_P, e))
        else:
            generals.append((ctx_P, e))

    if not indexes:
        return False, []

    if max(indexes, default=-1) + 1 - len(indexes) > 1:
        # if there is more than one missing
        raise ResolveError("Index missing on text definition.")

    error = False
    i = 0
    result = []
    while i <= max(indexes):
        ctx_rules = generals[:]
        if i in indexes:
            ctx_rules.extend(indexes[i])

        node = _resolve_ctx("t%d"%i, ctx_rules)
        error |= node is None
        result.append(node)
        i += 1

    return error, result


def _build_deps_topic(rules):
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
            raise ResolveError("A topic must be defined by a single coordinate.")

        if actual_P.index is not None:
            result[actual_P.kind]['indexes'][actual_P.index].append((ctx_P, e))
        else:
            result[actual_P.kind]['generals'].append((ctx_P, e))

    error = False
    for k in result:
        # k for kind (r or f)

        indexes = result[k]['indexes']
        generals = result[k]['generals']

        if not indexes and not generals:
            result[k] = []
            continue

        if max(indexes, default=-1) + 1 > len(indexes) + len(generals):
            # if there is more than one missing
            raise ResolveError("Index missing on topic definition.")

        current = []
        length = len(indexes) + len(generals)
        generals = generals.__iter__()
        for i in range(length):
            if i in indexes:
                ctx_rules = indexes[i]
            else:
                ctx_rules = [next(generals)]

            node = _resolve_ctx("%s%d"%(k, i), ctx_rules)
            error |= node is None

            current.append(node)

        result[k] = current

    return error, result


def _inferred_types(path, e):
    result = set()
    for inf in path.context.switch:
        if isinstance(e, tuple(path.context.switch[inf])):
            result.add(inf)

    if result:
        return result

    raise ResolveError("No compatible type found with the path %s and the ieml object of type %s"%
                     (str(path), e.__class__.__name__))


_errors = []
_context_stack = []
debug = False


def _context_error_handler(func):
    def wrapper(_path, rules):
        _context_stack.append(_path)

        result = None
        if debug:
            result = func(rules)
        else:
            try:
                result = func(rules)
            except ResolveError as e:
                _errors.append((':'.join(_context_stack[1:]), str(e)))
            except InvalidIEMLObjectArgument as e:
                _errors.append((':'.join(_context_stack[1:]), str(e)))

        _context_stack.pop()

        return result

    return wrapper


@_context_error_handler
def _resolve_ctx(rules):
    """
    Resolve the context of the rules (the type of this element), and building the ieml element.
    :param rules:
    :return:
    """
    if not rules:
        raise ResolveError("Missing node definition.")

    # if rules == [(None, e)] --> e
    if len(rules) == 1 and rules[0][0] is None:
        return rules[0][1]

    if any(r[0] is None for r in rules):
        raise ResolveError("Multiple definition, multiple ieml object provided for the same node.")

    if any(not isinstance(r[0], Path) for r in rules):
        raise ResolveError("Must have only path instance.")

    # resolve all the possible types for this element
    r0 = rules[0]
    types = _inferred_types(*r0)
    for r in rules[1:]:
        types = types.intersection(_inferred_types(*r))

    if not types:
        raise ResolveError("No definition, no type inferred on rules list.")

    if len(types) > 1:
        raise ResolveError("Multiple definition, multiple type inferred on rules list.")

    type = next(types.__iter__())

    if type == Topic:
        error, deps = _build_deps_topic(rules)
        if error:
            return

        flexing = None
        if deps['f']:
            flexing = deps['f']
        if not deps['r']:
            raise ResolveError("No root for the topic node.")

        return topic(deps['r'], flexing)

    if type == Text:
        error, deps = _build_deps_text(rules)
        if error:
            return

        return text(deps)

    if type in (Theory, Fact):
        error, deps = _build_deps_tree_graph(rules)
        if error:
            return

        if type == Fact:
            clauses = []
            for s, a, m in deps:
                clauses.append((s, a, m))
            return fact(clauses)
        else:
            clauses = []
            for s, a, m in deps:
                clauses.append((s, a, m))
            return theory(clauses)

    raise ResolveError("Invalid type inferred %s"%type.__name__)


def resolve_ieml_object(paths, elements=None):
    global _errors, _context_stack
    _errors = []
    _context_stack = []

    if isinstance(paths, dict):
        paths = list(paths.items())

    if elements is None:
        result = _resolve_ctx('', [(d, ieml(e)) for p, e in paths for d in path(p).develop])
    else:
        result = _resolve_ctx('', [(d, ieml(e)) for e, p in zip(elements, paths) for d in path(p).develop])

    if _errors:
        raise IEMLObjectResolutionError(_errors)

    return result

