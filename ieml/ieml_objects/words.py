from ieml.ieml_objects.paths import IEMLCoordinate
from ieml.exceptions import InvalidPathException
from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.constants import MORPHEME_SIZE_LIMIT
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument
from ieml.ieml_objects.terms import Term


class Morpheme(IEMLObjects):
    def __init__(self, children):
        if isinstance(children, Term):
            _children = (children,)
        else:
            try:
                _children = tuple(e for e in children)
            except TypeError:
                raise InvalidIEMLObjectArgument(Morpheme, "The argument %s is not an iterable" % str(children))

        if not 0 < len(_children) <= MORPHEME_SIZE_LIMIT:
            raise InvalidIEMLObjectArgument(Morpheme, "Invalid terms count %d."%len(_children))

        if not all((isinstance(e, Term) for e in _children)):
            raise InvalidIEMLObjectArgument(Morpheme, "%s do not contain only Term instances."%(str(_children)))

        # check singular sequences intersection
        singular_sequences = [s for t in _children for s in t.script.singular_sequences]
        if len(singular_sequences) != len(set(singular_sequences)):
            raise InvalidIEMLObjectArgument(Morpheme, "Singular sequences intersection in %s."%
                                            str([str(t) for t in _children]))

        super().__init__(sorted(_children))

    @property
    def grammatical_class(self):
        return max(t.grammatical_class for t in self.children)

    @property
    def empty(self):
        return len(self.children) == 1 and self.children[0].empty

    def compute_str(self, children_str):
        return '('+'+'.join(children_str)+')'

    def _resolve_coordinates(self, coordinate):
        if not isinstance(coordinate, TermCoordinate):
            raise ValueError("Must be a term coordinate %s."%str(coordinate))

        if any(c not in self.children for c in coordinate.objects):
            raise InvalidPathException(self, coordinate)

        return coordinate.objects

    def _coordinates_children(self):
        return [(TermCoordinate(t), t) for t in self.children]


class Word(IEMLObjects):
    closable = True

    def __init__(self, root=None, flexing=None, literals=None, children=None):

        if root is not None:
            _children = (root,) + ((flexing,) if flexing else ())
        else:
            _children = tuple(children)

        for c in _children:
            if not isinstance(c, Morpheme):
                raise InvalidIEMLObjectArgument(Word,
                                            "The children %s of a word must be a Morpheme instance." % (str(c)))

        # the root of a word can't be empty
        if _children[0].empty:
            raise InvalidIEMLObjectArgument(Word, "The root of a Word cannot be empty (%s)."%str(_children[0]))

        super().__init__(_children, literals=literals)

    @property
    def grammatical_class(self):
        return self.root.grammatical_class

    @property
    def root(self):
        return self.children[0]

    @property
    def flexing(self):
        if len(self.children) > 1:
            return self.children[1]
        return None

    def compute_str(self, children_str):
        return '['+'*'.join(children_str)+']'

    def _resolve_coordinates(self, coordinate):
        if not isinstance(coordinate, WordCoordinate):
            raise ValueError("Must be a word coordinate %s."%str(coordinate))
        return ((self.root,) if 'r' in coordinate.types else ()) +\
               ((self.flexing,) if 'f' in coordinate.types else ())

    def _coordinates_children(self):
        return [(WordCoordinate('r'), self.root)] + [(WordCoordinate('f'), self.flexing)] if self.flexing else []


class WordCoordinate(IEMLCoordinate):
    def __init__(self, v):
        if isinstance(v, str):
            self.types = v,
        else:
            try:
                self.types = tuple(sorted(set(v)))
            except TypeError:
                raise ValueError("A word coordinate must be initialised with an iterable or 'r' or 'f'.")

        if any(k not in ('r', 'f') for k in self.types):
            raise ValueError("A word coordinate must be r or f, not %s"%str(v))
        super().__init__()

    def __str__(self):
        return '+'.join(self.types)

    def _do_add(self, other):
        return WordCoordinate(self.types + other.types)

    def __eq__(self, other):
        return self.types == other.types

    def __hash__(self):
        return hash(self.types)


class TermCoordinate(IEMLCoordinate):
    def __init__(self, terms):
        if isinstance(terms, Term):
            self.objects = terms,
        else:
            try:
                self.objects = tuple(sorted(set(terms)))
            except TypeError:
                raise ValueError("A term coordinate must be initialised with an iterable of term or a term")

        super().__init__()

    def __str__(self):
        return '+'.join(map(str,self.objects))

    def _do_add(self, other):
        return TermCoordinate(self.objects + other.objects)

    def __eq__(self, other):
        return self.objects == other.objects

    def __hash__(self):
        return hash(self.objects)