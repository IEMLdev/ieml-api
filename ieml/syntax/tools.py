from ieml.dictionary.terms import Term
from ieml.syntax.parser.parser import IEMLParser
from ieml.syntax.words import Word, Morpheme


def proposition(arg, dictionary=None):
    if isinstance(arg, str):
        arg = IEMLParser().parse(arg)

    if isinstance(arg, Term):
        return Word(root=Morpheme([arg]))

    return arg