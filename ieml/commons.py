from .exceptions import InvalidIEMLObjectArgument


class cached_property:
    def __init__(self, factory):
        self._factory = factory
        self._attr_name = factory.__name__

    def __get__(self, instance, owner):
        attr = self._factory(instance)
        setattr(instance, self._attr_name, attr)
        return attr

class TreeStructure:
    def __init__(self):
        super().__init__()
        self._str = None
        self._paths = None
        self.children = None  # will be an iterable (list or tuple)

    def __str__(self):
        return self._str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, (TreeStructure, str)):
            return False

        return self._str == str(other)

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __iter__(self):
        """Enables the syntactic sugar of iterating directly on an element without accessing "children" """
        return self.children.__iter__()

    def tree_iter(self):
        yield self
        for c in self.children:
            yield from c.tree_iter()


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
