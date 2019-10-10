from ieml.usl import USL
from ieml.usl.constants import check_address_script
from ieml.usl.lexeme import Lexeme, class_from_address, check_lexeme
from ieml.usl.polymorpheme import PolyMorpheme
from ieml.usl.syntagmatic_function import SyntagmaticFunction


def check_word(w):
    if not isinstance(w.address, PolyMorpheme):
        raise ValueError("An address of a word is expected to be a polymorpheme, not a {}."
                         .format(w.address.__class__.__name__))

    check_address_script(w.address.constant)

    if not isinstance(w.syntagmatic_fun, SyntagmaticFunction):
        raise ValueError("The word is expected to be made from a SyntagmaticFunction, not a {}."
                         .format(w.syntagmatic_fun.__class__.__name__))

    w.syntagmatic_fun.check(Lexeme, check_lexeme)


class Word(USL):
    def __init__(self, syntagmatic_fun: SyntagmaticFunction, role: PolyMorpheme):
        super().__init__()
        self.syntagmatic_fun = syntagmatic_fun
        self.role = role

        self._singular_sequences = None
        self._singular_sequences_set = None

        self._str = self.syntagmatic_fun.render(self.role)

        self.grammatical_class = class_from_address(self.role)

    def _compute_singular_sequences(self):
        return [self]
