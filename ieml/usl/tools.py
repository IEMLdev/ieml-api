import random

from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.sentences import Sentence, SuperSentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator
from ieml.ieml_objects.words import Word, Morpheme
from ieml.usl.parser.parser import USLParser
from ieml.usl.usl import Usl


def usl(arg):
    if isinstance(arg, Usl):
        return arg
    if isinstance(arg, IEMLObjects):
        if isinstance(arg, Term):
            return Usl(Word(Morpheme([arg])))
        return Usl(arg)
    if isinstance(arg, str):
        return USLParser().parse(arg)

_ieml_objects_types = [Term, Word, Sentence, SuperSentence]
_ieml_object_generator = RandomPoolIEMLObjectGenerator(level=Text)

def random_usl():
    i = random.randint(0, 10)
    if i < 4:
        return usl(_ieml_object_generator.from_type(_ieml_objects_types[i]))

    return usl(_ieml_object_generator.text())