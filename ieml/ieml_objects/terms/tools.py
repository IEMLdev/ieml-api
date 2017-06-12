from ieml.ieml_objects.terms.version import DictionaryVersion
from ieml.script import Script
from ieml.ieml_objects.terms.terms import Term
from ieml.ieml_objects.terms.dictionary import Dictionary


class TermNotFoundInDictionary(Exception):
    def __init__(self, term, dictionary):
        self.message = "Cannot find term %s in the dictionary %s" % (str(term), str(dictionary.version))

    def __str__(self):
        return self.message


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

