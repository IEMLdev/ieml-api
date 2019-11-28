from itertools import product

from ieml.commons import LastUpdatedOrderedDict
from ieml.usl import USL
from ieml.usl.word import Word, check_word


def check_phrase(w):
    check_word(w.substance)
    check_word(w.attribute)
    check_word(w.mode)


class Phrase(USL):
    """(character*character*character)"""
    def __init__(self, substance: Word, attribute: Word, mode: Word):
        super().__init__()

        self.substance = substance
        self.attribute = attribute
        self.mode = mode
        self._str = '({})'.format("*".join([str(self.substance), str(self.attribute), str(self.mode)]))

    @property
    def empty(self):
        return self.substance.empty and self.attribute.empty and self.mode.empty

    def _compute_singular_sequences(self):
        if all(t.cardinal == 1 for t in [self.substance, self.attribute, self.mode]):
            return [self]

        words = LastUpdatedOrderedDict()

        for s, a, m in product(self.substance.singular_sequences,
                          self.attribute.singular_sequences,
                          self.mode.singular_sequences):

            w = Phrase(substance=s, attribute=a, mode=m)
            words[str(w)] = w

        return tuple(words.values())
