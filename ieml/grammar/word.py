from ieml.commons import TreeStructure
from ieml.dictionary import Term, term, Dictionary
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.grammar.usl import Usl


def word(arg, literals=None):
    if isinstance(arg, Word):
        if arg.literals != literals and literals is not None:
            return Word(arg.term, literals=literals)
        else:
            return arg
    else:
        return Word(term(arg), literals=literals)


class Word(Usl):
    def __init__(self, term, literals=None):
        if not isinstance(term, Term):
            raise InvalidIEMLObjectArgument(Word, "Invalid term {0} to create a Word instance.".format(str(term)))

        self.term = term
        self.dictionary_version = term.dictionary.version

        super().__init__(self.dictionary_version, literals=literals)

    __hash__ = TreeStructure.__hash__

    def compute_str(self):
        return str(self.term)

    def __getattr__(self, item):
        # make the term api accessible
        if item not in self.__dict__:
            return getattr(self.term, item)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.index == other.index

    def __gt__(self, other):
        if self.__class__ != other.__class__:
            return self.__class__ > other.__class__

        return self.index > other.index

    def _get_words(self):
        return {self}

    def _get_topics(self):
        return {}

    def _get_facts(self):
        return {}

    def _get_theories(self):
        return {}

    def _set_version(self, version):
        self.term = Dictionary(version).translate_script_from_version(self.term.dictionary.version, self.term.script)
