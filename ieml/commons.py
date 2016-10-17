from ieml.exceptions import InvalidPathException


class TreeStructure:
    def __init__(self):
        super().__init__()
        self._str = None
        self.children = None  # will be an iterable (list or tuple)

    def __str__(self):
        return self._str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """Two propositions are equal if their children'list or tuple are equal"""
        if not isinstance(other, TreeStructure):
            return False

        return self._str == other._str

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __iter__(self):
        """Enables the syntaxic sugar of iterating directly on an element without accessing "children" """
        return self.children.__iter__()

    def tree_iter(self):
        yield self
        for c in self.children:
            yield from c.tree_iter()

    def path(self, path):
        if len(path) == 0:
            return self

        p = path[0]
        if p in self.children:
            return p.path(path[1:])

        raise InvalidPathException(self, path)
