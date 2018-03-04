from functools import reduce
from operator import mul

from ieml.grammar.word import Word, word
from .usl import Usl
from ..exceptions import InvalidIEMLObjectArgument
from ..constants import MAX_SINGULAR_SEQUENCES, MORPHEME_SIZE_LIMIT


def topic(root, flexing=None, literals=None):
    root = _check_morpheme(root)

    if flexing is not None:
        flexing = _check_morpheme(flexing)
    else:
        flexing = tuple()

    # the root of a word can't be empty
    dictionary_version = root[0].dictionary_version

    for c in root + flexing:
        if c.dictionary_version != dictionary_version:
            raise InvalidIEMLObjectArgument(Topic, "Different dictionary version used in this topic.")

    return Topic(root, flexing, literals=literals)


def _check_morpheme(words):
    try:
        _words = [word(e) for e in words]
    except TypeError:
        raise InvalidIEMLObjectArgument(Topic, "The root argument %s is not an iterable" % str(words))

    if not 0 < len(_words) <= MORPHEME_SIZE_LIMIT:
        raise InvalidIEMLObjectArgument(Topic, "Invalid words count %d,"
                                               " must be greater than 0 and lower than %d."
                                        % (len(_words), MORPHEME_SIZE_LIMIT))

    if any(not isinstance(c, Word) for c in _words):
        raise InvalidIEMLObjectArgument(Topic, "The children of a Topic must be a Word instance.")

    singular_sequences = [s for t in _words for s in t.script.singular_sequences]
    if len(singular_sequences) != len(set(singular_sequences)):
        raise InvalidIEMLObjectArgument(Topic, "Singular sequences intersection in %s." %
                                            str([str(t) for t in _words]))

    return tuple(sorted(_words))


class Topic(Usl):
    def __init__(self, root, flexing, literals=None):

        self.root = root
        self.flexing = flexing

        super().__init__(self.root[0].dictionary_version, literals=literals)

        self.cardinal = reduce(mul, [s.script.cardinal for s in self.root + self.flexing])

        if self.cardinal > MAX_SINGULAR_SEQUENCES:
            raise InvalidIEMLObjectArgument(Topic, "Too many Topic- singular sequences defined (max: 360): %d"%self.cardinal)

    @property
    def grammatical_class(self):
        return self.root[0].grammatical_class

    def compute_str(self):
        return "[{0}]".format("*".join(
            "({0})".format("+".join(str(e) for e in s))
                for s in (self.root,) + ((self.flexing,) if self.flexing else tuple())
        ))

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