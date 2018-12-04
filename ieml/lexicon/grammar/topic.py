from functools import reduce
from itertools import zip_longest
from operator import mul

from ieml.lexicon.grammar.morpheme import Morpheme
from ieml.lexicon.grammar.word import Word, word
from .usl import Usl
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.constants import MAX_SINGULAR_SEQUENCES, MORPHEME_SIZE_LIMIT


def topic(root, flexing=None, literals=None):

    if not isinstance(root, Morpheme):
        raise InvalidIEMLObjectArgument(Topic, "The root argument must be a morpheme instance.")

    if flexing is not None:
        if not isinstance(flexing, Morpheme):
            raise InvalidIEMLObjectArgument(Topic, "The flexion argument must be a morpheme instance.")

        if flexing.dictionary_version != root.dictionary_version:
            raise InvalidIEMLObjectArgument(Topic, "Different dictionary version used in this topic.")
    else:
        flexing = None

    return Topic(root, flexing, literals=literals)


class Topic(Usl):
    def __init__(self, substance, attribute, mode, literals=None):
        self.substance = substance
        self.attribute = attribute
        self.mode = mode

        super().__init__(self.attribute.dictionary_version, literals=literals)

        self.cardinal = self.substance.cardinal * self.attribute.cardinal * self.mode.cardinal

        if self.cardinal > MAX_SINGULAR_SEQUENCES:
            raise InvalidIEMLObjectArgument(Topic, "Too many Topic- singular sequences defined (max: 360): %d"%self.cardinal)

    @property
    def grammatical_class(self):
        return self.root.grammatical_class

    def compute_str(self):
        if self.flexing:
            return "[{0}*{1}]".format(str(self.root), str(self.flexing))
        else:
            return "[{0}]".format(str(self.root))

    def _do_gt(self, other):
        return self.root > other.root if self.root != other.root else self.flexing > other.flexing

    def __iter__(self):
        return self.words.__iter__()

    def _get_words(self):
        return set(self.root + self.flexing)

    def _get_topics(self):
        return {self}

    def _get_facts(self):
        return {}

    def _get_theories(self):
        return {}

    def _set_version(self, version):
        for r in self.root:
            r.set_dictionary_version(version)

        for f in self.flexing:
            f.set_dictionary_version(version)

    def __repr__(self, lang='en'):
        row_format = "{:50s}" * 2
        print(row_format.format("root", "flexion"))

        clip = lambda s, n: s[:n-3] + '..' if len(s) > n else s
        res = ''
        for r, f in zip_longest(self.root, self.flexing, fillvalue=""):
            if r:
                r = clip(r.__repr__(lang=lang), 50)
            if f:
                f = clip(f.__repr__(lang=lang), 50)
            res += "{}\n".format(row_format.format(r,f))

        return res