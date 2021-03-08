from itertools import chain
from typing import Type

from ieml.dictionary.script import Script
from ieml.usl import USL
from ieml.usl.constants import check_address_script, class_from_address
from ieml.usl.lexeme import Lexeme, check_lexeme
from ieml.usl.syntagmatic_function import SyntagmaticFunction, SyntagmaticRole, DependantQualitySyntagmaticFunction, \
    IndependantQualitySyntagmaticFunction


def check_word(w: 'Word'):
    if not isinstance(w.role, SyntagmaticRole):
        raise ValueError("An address of a word is expected to be a polymorpheme, not a {}."
                         .format(w.role.__class__.__name__))

    check_address_script(w.role.constant, sfun_type=w.syntagmatic_fun.__class__)

    if not isinstance(w.syntagmatic_fun, SyntagmaticFunction):
        raise ValueError("The word is expected to be made from a SyntagmaticFunction, not a {}."
                         .format(w.syntagmatic_fun.__class__.__name__))

    w.syntagmatic_fun.check(Lexeme, check_lexeme, sfun_type=w.syntagmatic_fun.__class__)


def simplify_word(w: 'Word') -> 'Word':
    """remove empty leaves"""

    res = []
    word_role = w.role.constant if w.syntagmatic_fun.__class__ not in [DependantQualitySyntagmaticFunction, IndependantQualitySyntagmaticFunction] else \
        w.role.constant[1:]

    for r, sfun in w.syntagmatic_fun.actors.items():
        if all(l.actor.empty for l in sfun.actors.values() if l.actor is not None) and \
                (len(word_role) < len(r.constant) or any(rw != rn for rw, rn in zip(word_role, r.constant))):
            continue

        res.append([r.constant, sfun.actor])

    sfun = w.syntagmatic_fun._from_list(res)

    return Word(sfun, role=w.role, context_type=w.syntagmatic_fun.__class__)

class Word(USL):
    syntactic_level = 3

    def __init__(self, syntagmatic_fun: SyntagmaticFunction, role: SyntagmaticRole, context_type: Type[SyntagmaticFunction]):
        super().__init__()
        self.syntagmatic_fun = syntagmatic_fun
        self.role = role

        self._singular_sequences = None
        self._singular_sequences_set = None

        self._str = self.syntagmatic_fun.render_with_context(self.role, context=context_type)
        self.context_type = context_type

        self.grammatical_class = class_from_address(self.role)

    def _compute_singular_sequences(self):
        sfun_ss = self.syntagmatic_fun.singular_sequences(context_type=self.context_type)
        if len(sfun_ss) == 1:
            return [self]

        return [Word(sfun, self.role, self.context_type) for sfun in sfun_ss]

    def iter_structure(self):
        yield from self.syntagmatic_fun.iter_structure()

    def iter_structure_path(self, flexion=False):
        from ieml.usl.decoration.path import UslPath

        yield (UslPath(), self)
        yield from self.syntagmatic_fun.iter_structure_path(self.context_type, focus_role=self.role)

    @property
    def empty(self):
        return self.syntagmatic_fun.empty

    def do_lt(self, other):
        return self.syntagmatic_fun < other.syntagmatic_fun or \
               (self.syntagmatic_fun == other.syntagmatic_fun and self.role < other.role)

    @property
    def morphemes(self):
        return sorted(set(chain.from_iterable(e.actor.morphemes
                                              for e in self.syntagmatic_fun.actors.values())))

    def check(self):
        check_word(self)