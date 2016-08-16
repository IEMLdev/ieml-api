from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.constants import MORPHEME_SIZE_LIMIT
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument
from ieml.ieml_objects.terms import Term


class Morpheme(IEMLObjects):
    def __init__(self, term_list):
        super().__init__()

        try:
            _children = tuple(e for e in term_list)
        except TypeError:
            raise InvalidIEMLObjectArgument(Morpheme, "The argument %s is not an iterable"%str(term_list))

        if not 0 < len(_children) <= MORPHEME_SIZE_LIMIT:
            raise InvalidIEMLObjectArgument(Morpheme, "Invalid terms count %d."%len(_children))

        if not all((isinstance(e, Term) for e in _children)):
            raise InvalidIEMLObjectArgument(Morpheme, "%s do not contain only Term instances."%(str(_children)))

        # check singular sequences intersection
        singular_sequences = [t.script.singular_sequences for t in _children]
        if sum((len(e) for e in singular_sequences)) != len(set((e for e in singular_sequences))):
            raise InvalidIEMLObjectArgument(Morpheme, "Singular sequences intersection in %s."%
                                            str([str(t) for t in _children]))

        self.children = tuple(sorted(_children))

    @property
    def grammatical_class(self):
        return max(t.grammatical_class for t in self.children)

    @property
    def empty(self):
        return len(self.children) == 1 and self.children[0].empty


class Word(IEMLObjects):
    def __init__(self, root, flexing=None):
        super().__init__()

        if not isinstance(root, Morpheme):
            raise InvalidIEMLObjectArgument(Word, "The root %s of a word must be a Morpheme instance."%(str(root)))

        if flexing is not None:
            if not isinstance(flexing, Morpheme):
                raise InvalidIEMLObjectArgument(Word,
                                                "The flexing %s of a word must be a Morpheme instance." % (str(flexing)))
            self.children = (root, flexing)
        else:
            self.children = (root,)

        # the root of a word can't be empty
        if self.children[0].empty:
            raise InvalidIEMLObjectArgument(Word, "The root of a Word cannot be empty (%s)."%str(self.children[0]))

    @property
    def grammatical_class(self):
        return self.children[0].grammatical_class


