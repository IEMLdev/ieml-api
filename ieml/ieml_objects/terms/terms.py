from collections import namedtuple

from ieml.commons import LANGUAGES, cached_property
from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.terms.relations import Relations
from ieml.script.operator import script as _script

Translations = namedtuple('Translations', list(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)


class Term(IEMLObjects):
    closable = True

    def __init__(self, script, index, dictionary):
        self.dictionary = dictionary
        # from ieml.ieml_objects.terms.dictionary import Dictionary
        # if not isinstance(dictionary, Dictionary):
        #     raise ValueError("Invalid dictionary argument for Term creation: %s"%str(dictionary))

        # self.table = table
        # from ieml.ieml_objects.terms.table import AbstractTable
        # if not isinstance(table, AbstractTable):
        #     raise ValueError("Invalid table argument for Term creation: %s"%str(table))

        self.script = _script(script)
        super().__init__([])

        self.relations = Relations(term=self, dictionary=self.dictionary)
        self.index = index

        # if term in a dictionary, those values will be set
        self.translations = Translations(**{l: self.dictionary.translations[l][self.script] for l in LANGUAGES})

    __hash__ = IEMLObjects.__hash__

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return self.script == other.script

    def _do_gt(self, other):
        return self.script > other.script

    def compute_str(self, children_str):
        return "[" + str(self.script) + "]"

    @cached_property
    def root(self):
        return self.dictionary.get_root(self.script)

    @property
    def inhibitions(self):
        return self.dictionary.inhibitions[self.root]

    @cached_property
    def rank(self):
        return self.table.rank

    @property
    def empty(self):
        return self.script.empty

    @cached_property
    def ntable(self):
        return sum(self.script.cells[i].shape[2] for i in range(len(self.script.cells)))

    @cached_property
    def tables_term(self):
        return [self.dictionary.terms[s] for s in self.script.tables_script]

    @property
    def grammatical_class(self):
        return self.script.script_class

    @cached_property
    def singular_sequences(self):
        return [self.dictionary.terms[ss] for ss in self.script.singular_sequences]

    @property
    def layer(self):
        return self.script.layer

    @cached_property
    def table(self):
        return self.dictionary.tables[self.root][self]

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

    def __iter__(self):
        return self.singular_sequences.__iter__()
