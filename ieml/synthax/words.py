from ..commons import IEMLObjects
from ..exceptions import InvalidIEMLObjectArgument
from ..dictionary import Term
from ..constants import MAX_SINGULAR_SEQUENCES, MORPHEME_SIZE_LIMIT


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

        self.cardinal = 1
        for c in self.children:
            self.cardinal *= c.script.cardinal

    @property
    def grammatical_class(self):
        return max(t.grammatical_class for t in self.children)

    @property
    def empty(self):
        return len(self.children) == 1 and self.children[0].empty

    def compute_str(self, children_str):
        return '('+'+'.join(children_str)+')'


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

        self.cardinal = self.root.cardinal * (self.flexing.cardinal if self.flexing is not None else 1)
        if self.cardinal > MAX_SINGULAR_SEQUENCES:
            raise InvalidIEMLObjectArgument(Word, "Too many word- singular sequences defined (max: 360) here: %d"%self.cardinal)

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
