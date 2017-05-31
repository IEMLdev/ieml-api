import bidict


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

LAYER_MARKS = [
    ':',
    '.',
    '-',
    '\'',
    ',',
    '_',
    ';'
]

GRAMMATICAL_CLASS_NAMES = bidict.bidict({
    0: 'AUXILIARY',
    1: 'VERB',
    2: 'NOUN'
})

LANGUAGES = {
    'fr',
    'en'
}