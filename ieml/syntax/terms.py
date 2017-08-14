from ieml.commons import TreeStructure
from ieml.syntax.commons import IEMLSyntax


class SyntaxTerm(IEMLSyntax):
    """
    Mapping {dictionary version -> Term}

    If multiple term are equivalent (under different dictionary versions), they share the same SyntaxTerm

    The instances of this class are determined by the last DictionaryVersion (ref. all the updates made by versions)
    """

    def __init__(self, term, literals=None):
        self.term = term
        self.dictionary_version = term.dictionary.version

        super().__init__(children=(), literals=literals)

    __hash__ = TreeStructure.__hash__

    def __str__(self):
        return str(self.term)

    def compute_str(self, children_str):
        return str(self)

    def set_dictionary_version(self, version):
        diff = version.diff_for_version(self.term.dictionary.version)
        self.term = diff[self.term]

    def __getattr__(self, item):
        if item not in self.__dict__:
            return getattr(self.term, item)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.index == other.index

    def __gt__(self, other):
        return self.index > other.index

