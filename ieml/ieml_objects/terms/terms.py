from collections import namedtuple
import numpy as np

from ieml.commons import LANGUAGES
from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.terms.relations import Relations
from ieml.script.operator import script
from ieml.script.tools import factorize

Translations = namedtuple('Translations', list(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)


class Term(IEMLObjects):
    closable = True

    def __init__(self, s, dictionary):
        self.dictionary = dictionary
        self.script = script(s)

        self.grammatical_class = self.script.script_class

        super().__init__([])
        self.relations = Relations(term=self, dictionary=self.dictionary)
        self.index = None

        # if term in a dictionary, those values will be set
        self._translations = None
        self._root = None

        from ieml.ieml_objects.terms.tools import TermNotFoundInDictionary

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
    def parent(self):
        if self in self.dictionary.parents:
            return self.dictionary.parents[self]

        return None

    @property
    def partitions(self):
        return self.dictionary.partitions[self]

    @property
    def inhibitions(self):
        return self.dictionary.inhibitions[self.root]

    @property
    def translations(self):
        if self._translations is None:
            self._translations = Translations(**{l: self.dictionary.translations[l][self] for l in LANGUAGES})
        return self._translations

    @property
    def root(self):
        if self._root is None:
            self._root = self.dictionary.get_root(self.script)
        return self._root

    @property
    def rank(self):
        if self not in self.dictionary.ranks:
            print(self)
        return self.dictionary.ranks[self]

    @property
    def empty(self):
        return self.script.empty

    @property
    def defined(self):
        return all(self.__getattribute__(p) is not None for p in
                   ['translation', 'inhibitions', 'root', 'index', 'relations', 'rank'])

    @property
    def ntable(self):
        return sum(self.script.cells[i].shape[2] for i in range(len(self.script.cells)))

    def cells(self):
        if self.ntable != 1:
            raise ValueError("Too many dimension to generate table.")

        return self.script.cells[0][:,:,0]

    def headers(self):
        cells = self.cells()

        rows = [factorize([s for s in c]) for c in cells]
        columns = [factorize([s for s in c]) for c in cells.transpose()]

        return rows, columns

    @property
    def tables(self):
        return self.script.tables

    @property
    def singular_sequences(self):
        from .tools import term
        return [term(ss, dictionary=self.dictionary) for ss in self.script.singular_sequences]

    @property
    def layer(self):
        return self.script.layer

    def __contains__(self, item):
        from .tools import term
        if not isinstance(item, Term):
            item = term(item, dictionary=self.dictionary)
        elif item.dictionary != self.dictionary:
            print("\t[!] Comparison between different dictionary.")
            return False

        return item.script in self.script

    def __len__(self):
        return self.script.cardinal
