from itertools import islice
from typing import Union, List

from ieml.constants import LANGUAGES
from ieml.dictionary.script import Script
from ieml.dictionary.script.script import NULL_SCRIPTS
from ieml.exceptions import InvalidIEMLObjectArgument


class IEMLSyntaxType(type):
    """This metaclass enables the comparison of class types, such as (Sentence > Word) == True"""

    def __init__(cls, name, bases, dct):
        child_list = ['Word', 'Topic', 'Fact', 'Theory', 'Text', ]#'Hypertext']

        if name in child_list:
            cls.__rank = child_list.index(name) + 1
        else:
            cls.__rank = 0

        super(IEMLSyntaxType, cls).__init__(name, bases, dct)

    def __hash__(self):
        return self.__rank

    def __eq__(self, other):
        if isinstance(other, IEMLSyntaxType):
            return self.__rank == other.__rank
        else:
            return False

    def __ne__(self, other):
        return not IEMLSyntaxType.__eq__(self, other)

    def __gt__(self, other):
        return IEMLSyntaxType.__ge__(self, other) and self != other

    def __le__(self, other):
        return IEMLSyntaxType.__lt__(self, other) and self == other

    def __ge__(self, other):
        return not IEMLSyntaxType.__lt__(self, other)

    def __lt__(self, other):
        return self.__rank < other.__rank

    def syntax_rank(self):
        return self.__rank


Literal = Union[List[str], str]


class Usl(metaclass=IEMLSyntaxType):
    def __init__(self, literals: Literal=None):
        super().__init__()
        self._paths = None

        _literals = []
        if literals is not None:
            if isinstance(literals, str):
                _literals = [literals]
            else:
                try:
                    _literals = tuple(literals)
                except TypeError:
                    raise InvalidIEMLObjectArgument(self.__class__, "The literals argument %s must be an iterable of "
                                                                    "str or a str."%str(literals))
        self.literals = tuple(_literals)
        self._str = self._compute_str()

    def _do_gt(self, other):
        raise NotImplementedError(self.__class__)

    def compute_str(self):
        raise NotImplementedError(self.__class__)

    def __str__(self):
        return self._str

    def __hash__(self):
        """Since the IEML string for any proposition AST is unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __gt__(self, other):
        if not isinstance(other, Usl):
            raise NotImplemented

        if self.__class__ != other.__class__:
            return self.__class__ > other.__class__

        return self._do_gt(other)

    def __eq__(self, other):
        if not isinstance(other, (Usl, str)):
            return False

        return self._str == str(other)

    def _compute_str(self):
        _literals = ''
        if self.literals:
            _literals = '<' + '><'.join(self.literals) + '>'

        return self.compute_str() + _literals

    def __getitem__(self, item):
        from ieml.lexicon.paths import Path, path, resolve

        if isinstance(item, str):
            item = path(item)

        if isinstance(item, Path):
            res = resolve(self, item)
            if len(res) == 1:
                return res.__iter__().__next__()
            else:
                return tuple(sorted(res))

        from .word import Word
        if item == Word:
            return self.semes

        from .word import Word
        if item == Word:
            return self.words

        from .fact import Fact
        if item == Fact:
            return self.facts

        from .theory import Theory
        if item == Theory:
            return self.theories

        from .text import Text
        if item == Text:
            return {self} if self.__class__ == Text else {}

    def __iter__(self):
        raise NotImplementedError()

    def __contains__(self, item):
        if not isinstance(item, Usl):
            raise ValueError("Invalid argument {0}".format(str(item)))

        from .word import Word
        if isinstance(item, Word):
            return item in self.semes

        from .word import Word
        if isinstance(item, Word):
            return item in self.words

        from .fact import Fact
        if isinstance(item, Fact):
            return item in self.facts

        from .theory import Theory
        if isinstance(item, Theory):
            return item in self.theories

        from .text import Text
        if isinstance(item, Text):
            return item.semes.issubset(self.semes) and \
                   item.words.issubset(self.words) and \
                   item.facts.issubset(self.facts) and \
                   item.theories.issubset(self.theories)

    def rules(self, type):
        from ieml.lexicon.paths import enumerate_paths
        return {path: element for path, element in enumerate_paths(self, level=type)}

    def objects(self, type):
        return set(self.rules(type).values())

    # @property
    # def dictionary(self):
    #     return Dictionary(self.dictionary_version)

    @property
    def paths(self):
        return self.rules(Script)

    def _get_cardinal(self):
        raise NotImplementedError()

    def _get_semes(self):
        raise NotImplementedError()

    def _get_words(self):
        raise NotImplementedError()

    def _get_facts(self):
        raise NotImplementedError()

    def _get_theories(self):
        raise NotImplementedError()

    @property
    def semes(self):
        return frozenset(set(self._get_semes()) - set(NULL_SCRIPTS))

    @property
    def words(self):
        return frozenset(self._get_words())

    @property
    def facts(self):
        return frozenset(self._get_facts())

    @property
    def theories(self):
        return frozenset(self._get_theories())

    # @property
    # def words_vector(self, dictionary):
    #     v = np.zeros(len(dictionary))
    #     v[[w.index for w in self.semes]] = 1
    #     return v

    @property
    def cardinal(self):
        return self._get_cardinal()

    def auto_translation(self):
        result = {}
        entries = sorted([t for p, t in self.paths.items()])
        for l in LANGUAGES:
            result[l] = ' '.join((e.translations[l] for e in islice(entries, 10)))

        return result

    def pretty_print(self):
        print(self.__repr__())

    
def usl(arg):
    if isinstance(arg, str):
        from ieml.lexicon.grammar.parser import IEMLParser
        return IEMLParser().parse(arg)

    if isinstance(arg, Script):
        from .word import word
        return word([arg])

    if isinstance(arg, Usl):
        return arg

    from ieml.lexicon.paths import resolve_ieml_object, path
    if isinstance(arg, dict):
        # map path -> Ieml_object
        return resolve_ieml_object(arg)

    # if iterable, can be a list of usl to convert into a text
    try:
        usl_list = list(arg)
    except TypeError:
        pass
    else:
        if len(usl_list) == 0:
            return usl('E:')

        if all(isinstance(u, Usl) for u in usl_list):
            if len(usl_list) == 1:
                return usl_list[0]
            else:
                from ieml.lexicon import text
                return text(usl_list)
        else:
            # list of path objects
            try:
                rules = [(a, b) for a, b in usl_list]
            except TypeError:
                pass
            else:
                rules = [(path(a), usl(b)) for a, b in rules]
                return resolve_ieml_object(rules)

    raise NotImplementedError()


TYPE_TO_ATTRIBUTE = {'Word': 'words',
                     'Topic': 'topics',
                     'Fact': 'facts',
                     'Theory': 'theories',
                     'Text': 'texts'}