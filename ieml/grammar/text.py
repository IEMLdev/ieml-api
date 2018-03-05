from itertools import chain

from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.grammar import topic
from ieml.grammar.usl import Usl
from ieml.grammar.fact import Fact
from ieml.grammar.theory import Theory
from ieml.grammar.topic import Topic
from ieml.grammar.word import Word

def text(children, literals=None):
    try:
        _children = [e for e in children]
    except TypeError:
        raise InvalidIEMLObjectArgument(Text, "The argument %s is not iterable." % str(children))

    if not all(isinstance(e, (Word, Topic, Fact, Theory, Text)) for e in _children):
        raise InvalidIEMLObjectArgument(Text, "Invalid type instance in the list of a text,"
                                              " must be Word, Sentence, SuperSentence or Text")

    return Text(_children, literals=literals)


class Text(Usl):
    def __init__(self, children, literals=None):

        _children = [topic([c]) if isinstance(c, Word) else c for c in children]
        _children = list(chain([c for c in _children if not isinstance(c, Text)],
                               *(c.children for c in _children if isinstance(c, Text))))
        self.children = sorted(set(_children))

        dictionary_version = self.children[0].dictionary_version
        if any(e.dictionary_version != dictionary_version for e in self.children):
            raise InvalidIEMLObjectArgument(Fact, "Incompatible dictionary version in the list of usls")

        super().__init__(dictionary_version, literals=literals)

    def compute_str(self):
        return '/{0}/'.format('//'.join(str(c) for c in self.children))

    def __iter__(self):
        return self.children.__iter__()

    def _get_words(self):
        return set(chain.from_iterable(c.words for c in self.children))

    def _get_topics(self):
        return set(chain.from_iterable(c.topics for c in self.children))

    def _get_facts(self):
        return set(chain.from_iterable(c.facts for c in self.children))

    def _get_theories(self):
        return set(chain.from_iterable(c.theories for c in self.children))

    def _set_version(self, version):
        for c in self.children:
            c.set_dictionary_version(version)
