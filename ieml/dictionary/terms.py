import logging
from collections import namedtuple
import re

from ieml.constants import PHONETIC_PUNCTUATION
from ..commons import cached_property
from ..constants import LANGUAGES
from .script import script as _script
logger = logging.getLogger(__name__)
Translations = namedtuple('Translations', list(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)


class Term:
    def __init__(self, script, index, dictionary, parent):
        super().__init__()

        self.dictionary = dictionary
        self.parent = parent

        self.script = _script(script)

        self.index = index

        # if term in a dictionary, those values will be set
        self.translations = Translations(**{l: self.dictionary.translations[l][self.script] for l in LANGUAGES})

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.index == other.index

    def __gt__(self, other):
        return self.index > other.index

    def __hash__(self):
        return hash(self.__str__())

    def __str__(self):
        return "[%s]" % str(self.script)

    _compute_str = __str__

    def tree_iter(self):
        yield self

    @cached_property
    def root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.root

    @property
    def is_root(self):
        return self in self.dictionary.roots

    @property
    def inhibitions(self):
        return self.dictionary.inhibitions[self.root]

    @cached_property
    def max_rank(self):
        if self.parent is None:
            # root
            return max(t.rank for t in self.relations.contains if len(t) != 1)

        return self.root.max_rank

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

    @cached_property
    def relations(self):
        return self.dictionary.relations_graph[self]

    def __contains__(self, item):
        from .tools import term
        if not isinstance(item, Term):
            item = term(item, dictionary=self.dictionary)
        elif item.dictionary != self.dictionary:
            logger.log(logging.ERROR, "Comparison between different dictionary.")
            return False

        return item.script in self.script

    def __len__(self):
        return self.script.cardinal

    def __iter__(self):
        return self.singular_sequences.__iter__()

    @property
    def phonetic(self):
        return re.sub('[^a-zA-Z]', '', self.__str__()) + PHONETIC_PUNCTUATION[self.layer]