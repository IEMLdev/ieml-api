from itertools import chain

from ieml.usl import USL
from ieml.usl.constants import check_address_script, class_from_address
from ieml.usl.lexeme import Lexeme, check_lexeme
from ieml.usl.syntagmatic_function import SyntagmaticFunction, SyntagmaticRole


def check_word(w: 'Word'):
    if not isinstance(w.role, SyntagmaticRole):
        raise ValueError("An address of a word is expected to be a polymorpheme, not a {}."
                         .format(w.role.__class__.__name__))

    check_address_script(w.role.constant)

    if not isinstance(w.syntagmatic_fun, SyntagmaticFunction):
        raise ValueError("The word is expected to be made from a SyntagmaticFunction, not a {}."
                         .format(w.syntagmatic_fun.__class__.__name__))

    w.syntagmatic_fun.check(Lexeme, check_lexeme)


class Word(USL):
    def __init__(self, syntagmatic_fun: SyntagmaticFunction, role: SyntagmaticRole):
        super().__init__()
        self.syntagmatic_fun = syntagmatic_fun
        self.role = role

        self._singular_sequences = None
        self._singular_sequences_set = None

        self._str = self.syntagmatic_fun.render(self.role)

        self.grammatical_class = class_from_address(self.role)

    def _compute_singular_sequences(self):
        return [self]

    def do_lt(self, other):
        return self.syntagmatic_fun < other.syntagmatic_fun or \
               (self.syntagmatic_fun == other.syntagmatic_fun and self.role < other.role)

    @property
    def morphemes(self):
        return sorted(set(chain.from_iterable(e.actor.morphemes
                                              for e in self.syntagmatic_fun.actors.values())))
