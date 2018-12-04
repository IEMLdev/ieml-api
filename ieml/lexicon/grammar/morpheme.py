from functools import reduce
from operator import mul

from ieml.constants import MORPHEME_SIZE_LIMIT
from ieml.exceptions import InvalidIEMLObjectArgument
from .usl import Usl
from .word import word, Word


def morpheme(words, literals=None):
    try:
        _words = [word(e) for e in words]
    except TypeError:
        raise InvalidIEMLObjectArgument(Morpheme, "The root argument %s is not an iterable" % str(words))

    if len(_words) > MORPHEME_SIZE_LIMIT:
        raise InvalidIEMLObjectArgument(Morpheme, "Invalid words count %d, must be lower or equal than %d."
                                        % (len(_words), MORPHEME_SIZE_LIMIT))
    if words == []:
        return Morpheme(tuple(), literals=literals)

    if any(not isinstance(c, Word) for c in _words):
        raise InvalidIEMLObjectArgument(Morpheme, "The children of a Topic must be a Word instance.")

    dict_version = words[0].dictionary_version
    if any(dict_version != w.dictionary_version for w in _words):
        raise InvalidIEMLObjectArgument(Morpheme, "Different dictionary version used in this morpheme.")

    singular_sequences = [s for t in _words for s in t.script.singular_sequences]
    if len(singular_sequences) != len(set(singular_sequences)):
        raise InvalidIEMLObjectArgument(Morpheme, "Singular sequences intersection in %s." %
                                        str([str(t) for t in _words]))

    return Morpheme(tuple(sorted(_words)), literals=literals)


class Morpheme(Usl):
    def __init__(self, words, literals=None):
        self._words = words

        super().__init__(self._words[0].dictionary_version, literals=literals)

    def _do_gt(self, other):
        return self._words > other._words

    @property
    def empty(self):
        return len(self._words) == 0

    @property
    def grammatical_class(self):
        return max(w.grammatical_class for w in self._words)

    def compute_str(self):
        return "({0})".format("+".join(str(e) for e in self._words))

    def __iter__(self):
        return self._words.__iter__()

    def _get_cardinal(self):
        return reduce(mul, [w.cardinal for w in self._words], initial=1)

    def _get_words(self):
        return set(self._words)

    def _get_topics(self):
        return {}

    def _get_facts(self):
        return {}

    def _get_theories(self):
        return {}

    def _set_version(self, version):
        for r in self._words:
            r.set_dictionary_version(version)

    def __repr__(self, lang='en'):
        return '\n'.join("{:80s}".format(
            "{0} ({1})".format(str(w), w.translations[lang])) for w in self._words)
