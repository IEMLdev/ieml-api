from ieml.commons import TreeStructure
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument

MORPHEME_SIZE_LIMIT = 12
MAX_NODES_IN_SENTENCE = 20
# TODO put the good value
MAX_DEPTH_IN_HYPERTEXT = 8
MAX_NODES_IN_HYPERTEXT = 20

class IEMLType(type):
    """This metaclass enables the comparison of class times, such as (Sentence > Word) == True"""

    def __init__(cls, name, bases, dct):
        child_list = ['Term', 'Morpheme', 'Word', 'Clause', 'Sentence',
                     'SuperClause', 'SuperSentence', 'Text', 'Hyperlink', 'Hypertext']
        if name in child_list:
            cls.__rank = child_list.index(name) + 1
        else:
            cls.__rank = 0

        super(IEMLType, cls).__init__(name, bases, dct)

    def __hash__(self):
        return self.__rank

    def __eq__(self, other):
        if isinstance(other, IEMLType):
            return self.__rank == other.__rank
        else:
            return False

    def __ne__(self, other):
        return not IEMLType.__eq__(self, other)

    def __gt__(self, other):
        return IEMLType.__ge__(self, other) and self != other

    def __le__(self, other):
        return IEMLType.__lt__(self, other) and self == other

    def __ge__(self, other):
        return not IEMLType.__lt__(self, other)

    def __lt__(self, other):
        return self.__rank < other.__rank

    def ieml_rank(self):
        return self.__rank


class IEMLObjects(TreeStructure, metaclass=IEMLType):
    closable = False

    def __init__(self, children, literals=None):
        super().__init__()
        self.children = tuple(children)

        _literals = []
        if literals is not None:
            if isinstance(literals, str):
                _literals = [literals]
            else:
                try:
                    _literals = tuple(literals)
                except TypeError:
                    raise InvalidIEMLObjectArgument(self.__class__, "The literals argument %s must be an iterable of "
                                                                    "str or a str."%str(literals))

        self.literals = tuple(_literals)
        self._do_precompute_str()

    def __gt__(self, other):
        if not isinstance(other, IEMLObjects):
            raise NotImplemented

        if self.__class__ != other.__class__:
            return self.__class__ > other.__class__

        return self._do_gt(other)

    def _do_gt(self, other):
        return self.children > other.children

    def compute_str(self, children_str):
        return '#'.join(children_str)

    def _compute_str(self):
        if self._str is not None:
            return self._str
        _literals = ''
        if self.literals:
            _literals = '<' + '><'.join(self.literals) + '>'
        return self.compute_str([e._compute_str() for e in self.children]) + _literals

    def _do_precompute_str(self):
        self._str = self._compute_str()
