from ..exceptions import TermNotFoundInDictionary
from .version import DictionaryVersion
from .script import Script
from .terms import Term
from .dictionary import Dictionary


def term(arg, dictionary=None):
    if isinstance(arg, Term):
        return arg

    if not isinstance(dictionary, Dictionary):
        if isinstance(dictionary, (str, DictionaryVersion)):
            dictionary = Dictionary(dictionary)
        else:
            dictionary = Dictionary()

    if isinstance(arg, int):
        return dictionary.index[arg]

    if isinstance(arg, str):
        if arg[0] == '[' and arg[-1] == ']':
            arg = arg[1:-1]

    if isinstance(arg, Script) or isinstance(arg, str):
        if arg in dictionary:
            return dictionary.terms[arg]

    raise TermNotFoundInDictionary(arg, dictionary)

