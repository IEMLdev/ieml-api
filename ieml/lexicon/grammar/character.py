from functools import reduce
from operator import mul
from typing import List, Union

from ieml.constants import CHARACTER_SIZE_LIMIT
from ieml.dictionary.script import script, Script
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.lexicon.grammar.usl import Literal
from .usl import Usl


def character(semes: List[Union[Script, str]], literals:Literal=None):
    try:
        _semes = [script(e) for e in semes]
    except TypeError:
        raise InvalidIEMLObjectArgument(Character, "The root argument %s is not an iterable" % str(semes))

    if len(_semes) > CHARACTER_SIZE_LIMIT:
        raise InvalidIEMLObjectArgument(Character, "Invalid semes count %d, must be lower or equal than %d."
                                        % (len(_semes), CHARACTER_SIZE_LIMIT))
    if _semes == []:
        return Character([], literals=literals)

    if any(not isinstance(c, Script) for c in _semes):
        raise InvalidIEMLObjectArgument(Character, "The children of a Topic must be a Word instance.")

    singular_sequences = [s for t in _semes for s in t.singular_sequences]
    if len(singular_sequences) != len(set(singular_sequences)):
        raise InvalidIEMLObjectArgument(Character, "Singular sequences intersection in %s." %
                                        str([str(t) for t in _semes]))

    return Character(_semes, literals=literals)


class Character(Usl):
    def __init__(self, semes: List[Script], literals: Literal=None):
        self._semes = sorted(semes)

        super().__init__(literals=literals)

    def _do_gt(self, other):
        return self._semes > other._semes

    @property
    def empty(self):
        return len(self._semes) == 0

    @property
    def grammatical_class(self):
        return max(w.script_class for w in self._semes)

    def compute_str(self):
        return "({0})".format("+".join("[{}]".format(str(e)) for e in self._semes))

    def __iter__(self):
        return self._semes.__iter__()

    def _get_cardinal(self):
        return reduce(mul, [w.cardinal for w in self._semes], initial=1)

    def _get_semes(self):
        return set(self._semes)

    def _get_words(self):
        return set()

    def _get_facts(self):
        return set()

    def _get_theories(self):
        return set()

    def __repr__(self, lang='en'):
        return '\n'.join("{:80s}".format(
            "{0} ({1})".format(str(w), w.translations[lang])) for w in self._semes)
