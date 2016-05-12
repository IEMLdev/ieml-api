from ieml.exceptions import CannotRenderElementWithoutOrdering


class PropositionPath:
    """Stores a path to a 'closable' proposition *inside* another closed proposition, in a text.
    Used by hyperlinks to figure out which proposition is the right one"""

    def __init__(self, path=None, proposition=None):
        self.path = []
        if path:
            self.path += path
        if proposition:
            self.path.append(proposition)

    def __str__(self):
        return '/'.join(self.to_ieml_list())

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.path == other.path

    def to_ieml_list(self):
        return [str(e) for e in self.path]


class TreeStructure:
    def __init__(self):
        super().__init__()
        self._has_been_checked = False
        self._has_been_ordered = False
        self._str = None
        self.childs = None  # will be an iterable (list or tuple)

    def _do_precompute_str(self):
        pass

    def _do_ordering(self):
        pass

    def order(self):
        if self.is_ordered():
            return

        self._do_ordering()
        self._do_precompute_str()
        self._has_been_ordered = True

    def _do_checking(self):
        pass

    def check(self):
        """Checks the IEML validity of the IEML proposition"""
        for child in self.childs:
            child.check()
            child.order()

        if self.is_checked():
            return

        self._do_checking()
        self._has_been_checked = True

        self.order()

    def is_checked(self):
        return self._has_been_checked

    def is_ordered(self):
        return self._has_been_ordered

    def __eq__(self, other):
        """Two propositions are equal if their childs'list or tuple are equal"""
        return self.childs == other.childs

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __str__(self):
        if self._str is not None:
            return self._str
        else:
            raise CannotRenderElementWithoutOrdering()
