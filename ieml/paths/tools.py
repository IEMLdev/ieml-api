from ieml.ieml_objects.sentences import SuperSentence, Sentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word
from ieml.paths.parser.parser import PathParser
from ieml.paths.paths import Path, Coordinate, MultiplicativePath


def path(p):
    if isinstance(p, Path):
        return p
    if isinstance(p, str):
        return PathParser().parse(p)

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

