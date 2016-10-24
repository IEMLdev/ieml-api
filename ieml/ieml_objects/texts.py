from ieml.ieml_objects.paths import IEMLPath, IEMLCoordinate
from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument
from ieml.ieml_objects.sentences import Sentence, SuperSentence
from ieml.ieml_objects.words import Word


class Text(IEMLObjects):
    closable = True

    def __init__(self, children):
        try:
            _children = [e for e in children]
        except TypeError:
            raise InvalidIEMLObjectArgument(Text, "The argument %s is not iterable." % str(children))

        if not all(isinstance(e, (Word, Sentence, SuperSentence)) for e in _children):
            raise InvalidIEMLObjectArgument(Text, "Invalid type instance in the list of a text,"
                                                  " must be Word, Sentence or SuperSentence.")

        super().__init__(sorted(set(_children)))

    def compute_str(self, children_str):
        return '{/' + '//'.join(children_str) + '/}'

    def _coordinates_children(self):
        return [(TextCoordinate(i), c) for i, c in enumerate(self.children)]

    def _resolve_coordinates(self, coordinate):
        return [self.children[i] for i in coordinate.indexes]


class TextCoordinate(IEMLCoordinate):

    def __init__(self, index):
        if isinstance(index, int):
            self.indexes = index,
        else:
            try:
                self.indexes = tuple(sorted(set(index)))
            except TypeError:
                raise ValueError("A TextCoordinate must be instantiated with a text index or an iterable of text index.")

        if any(not isinstance(e, int) for e in self.indexes):
            raise ValueError("A TextCoordinate must have integer text index.")

        super().__init__()

    def _do_add(self, other):
        return TextCoordinate(self.indexes + other.indexes)

    def __str__(self):
        return 't' + '+t'.join(map(str, self.indexes))

    def __eq__(self, other):
        return self.indexes == other.indexes

    def __hash__(self):
        return hash(self.indexes)