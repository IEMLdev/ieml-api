import random

from ieml.ieml_objects.commons import IEMLObjects, IEMLType
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


def random_usl(rank_type=None):
    if rank_type and not isinstance(rank_type, IEMLType):
        raise ValueError('The wanted type for the generated usl object must be a IEMLType, here : '
                         '%s'%rank_type.__class__.__name__)

    if not rank_type:
        i = random.randint(0, 10)
        if i < 4:
            rank_type = _ieml_objects_types[i]
        else:
            rank_type = Text

    return usl(_ieml_object_generator.from_type(rank_type))