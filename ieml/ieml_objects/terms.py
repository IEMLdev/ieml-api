from ieml.ieml_objects.commons import IEMLObjects
from ieml.script.operator import script


class Term(IEMLObjects):
    closable = True

    def __init__(self, s, dictionary):
        self.dictionary = dictionary
        self.script = script(s)

        self.grammatical_class = self.script.script_class

        super().__init__([])

        self._relations = {}

        # if term in a dictionary, those values will be set
        self.translation = None
        self.inhibitions = None
        self.root = None
        self.index = None
        self.relations = None
        self.rank = None
        self.parent = None

        self._rank = None

    __hash__ = IEMLObjects.__hash__

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return self.script == other.script

    def _do_gt(self, other):
        return self.script > other.script

    def compute_str(self, children_str):
        return "[" + str(self.script) + "]"

    @property
    def empty(self):
        return self.script.empty

    @property
    def defined(self):
        return all(self.__getattribute__(p) is not None for p in
                   ['translation', 'inhibitions', 'root', 'index', 'relations', 'rank'])

    @property
    def tables(self):
        return self.script.tables