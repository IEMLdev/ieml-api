from ieml.commons import TreeStructure
from ieml.dictionary.dictionary import Dictionary
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
        return self.term.__str__()

    def compute_str(self, children_str):
        return str(self)

    def set_dictionary_version(self, version):
        self._str = None
        self.term = Dictionary(version).translate_script_from_version(self.term.dictionary.version, self.term.script)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return getattr(self.term, item)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.index == other.index

    def __gt__(self, other):
        if self.__class__ != other.__class__:
            return self.__class__ > other.__class__

        return self.index > other.index

