from ieml.commons import TreeStructure
from ieml.exceptions import InvalidIEMLObjectArgument


class IEMLSyntaxType(type):
    """This metaclass enables the comparison of class times, such as (Sentence > Word) == True"""

    def __init__(cls, name, bases, dct):
        child_list = ['SyntaxTerm', 'Morpheme', 'Word', 'Clause', 'Sentence',
                      'SuperClause', 'SuperSentence', 'Text',
                      'Hyperlink', 'Hypertext']

        if name in child_list:
            cls.__rank = child_list.index(name) + 1
        else:
            cls.__rank = 0

        super(IEMLSyntaxType, cls).__init__(name, bases, dct)

    def __hash__(self):
        return self.__rank

    def __eq__(self, other):
        if isinstance(other, IEMLSyntaxType):
            return self.__rank == other.__rank
        else:
            return False

    def __ne__(self, other):
        return not IEMLSyntaxType.__eq__(self, other)

    def __gt__(self, other):
        return IEMLSyntaxType.__ge__(self, other) and self != other

    def __le__(self, other):
        return IEMLSyntaxType.__lt__(self, other) and self == other

    def __ge__(self, other):
        return not IEMLSyntaxType.__lt__(self, other)

    def __lt__(self, other):
        return self.__rank < other.__rank

    def syntax_rank(self):
        return self.__rank


class IEMLSyntax(TreeStructure, metaclass=IEMLSyntaxType):
    closable = False

    def __init__(self, children, literals=None):
        super().__init__()
        self.children = tuple(children)

        if self.children:
            dictionary_version = self.children[0].dictionary_version
            if any(dictionary_version != c.dictionary_version for c in self.children[1:]):
                raise InvalidIEMLObjectArgument(self.__class__, "Multiple dictionary versions for this syntax object.")

            self.dictionary_version = dictionary_version
        elif not hasattr(self, 'dictionary_version'):
            raise InvalidIEMLObjectArgument(self.__class__, "No dictionary version specified for this syntax object.")


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

    def set_dictionary_version(self, version):
        self.dictionary_version = version
        for c in self.children:
            c.set_dictionary_version(version)

        self._str = None
        self._do_precompute_str()

    def __gt__(self, other):
        if not isinstance(other, IEMLSyntax):
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

    def __getitem__(self, item):
        from ieml.usl.paths import Path, path, resolve

        if isinstance(item, str):
            item = path(item)

        if isinstance(item, Path):
            res = resolve(self, item)
            if len(res) == 1:
                return res.__iter__().__next__()
            else:
                return list(res)

        if isinstance(item, int):
            return self.children[item]

    def __len__(self):
        return len(self.children)
