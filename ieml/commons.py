

class TreeStructure:
    def __init__(self):
        super().__init__()
        self._str = None
        self.children = None  # will be an iterable (list or tuple)

    def __str__(self):
        if self._str is None:
            self._do_precompute_str()

        return self._str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """Two propositions are equal if their children'list or tuple are equal"""
        return self.children == other.children

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

    # @property
    # def level(self):
    #     """Returns the string level of an IEML object, such as TEXT, WORD, SENTENCE, ..."""
    #     return self.__class__.__name__.upper()

    # @property
    # def metadata(self):
    #     if self._metadata is None:
    #         self._metadata = self._retrieve_metadata_instance()
    #         if self._metadata is not None:
    #             return self._metadata
    #         else:
    #             raise CannotRetrieveMetadata("Cannot retrieve metadata for this element")
    #     else:
    #         return self._metadata

    def _do_precompute_str(self):
        pass