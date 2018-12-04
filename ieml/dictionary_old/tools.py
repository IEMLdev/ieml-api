from functools import singledispatch

from ieml.exceptions import TermNotFoundInDictionary
from .version import DictionaryVersion
from .script import Script
from .terms import Term
from .dictionary import Dictionary


def term(arg, dictionary=None):
    if not isinstance(dictionary, Dictionary):
        if isinstance(dictionary, (str, DictionaryVersion)):
            dictionary = Dictionary(dictionary)
        else:
            dictionary = Dictionary()

    try:
        return _term(arg, dictionary)
    except KeyError:
        raise TermNotFoundInDictionary(arg, dictionary)

@singledispatch
def _term(arg, dictionary):
    raise ValueError("Unsupported class %s for %s"%(arg.__class__.__name__, str(arg)))

_term.register(Term, lambda arg, dictionary: arg)
_term.register(int, lambda arg, dictionary: dictionary.index[arg])
_term.register(Script, lambda arg, dictionary: dictionary.terms[arg])

@_term.register(str)
def _term_str(arg, dictionary=None):
    if not arg:
        raise TermNotFoundInDictionary(arg, dictionary)

    if arg[0] == '[' and arg[-1] == ']':
        arg = arg[1:-1]

    return dictionary.terms[arg]
