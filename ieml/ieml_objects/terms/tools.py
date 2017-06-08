from ieml.script import Script
from ieml.ieml_objects.terms.terms import Term
from ieml.ieml_objects.terms.dictionary import Dictionary


class TermNotFoundInDictionary(Exception):
    def __init__(self, term):
        self.message = "Cannot find term %s in the dictionary" % str(term)

    def __str__(self):
        return self.message


def term(arg):
    if isinstance(arg, Term):
        return arg

    if isinstance(arg, int):
        return Dictionary().index[arg]

    if isinstance(arg, str):
        if arg[0] == '[' and arg[-1] == ']':
            arg = arg[1:-1]

    if isinstance(arg, Script) or isinstance(arg, str):
        d = Dictionary()
        if arg in d.terms:
            return d.terms[arg]

    print("Invalid argument for term creation %s (or not in dictionary)"%str(arg))
    raise TermNotFoundInDictionary(arg)

