from ieml.commons import TreeStructure
from ieml.dictionary import Term, term
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.grammar.usl import Usl


def word(arg, literals=None):
    if isinstance(arg, Word) and arg.literals == literals:
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

    @property
    def words(self):
        return {self}

    @property
    def topics(self):
        return {}

    @property
    def facts(self):
        return {}

    @property
    def theories(self):
        return {}
