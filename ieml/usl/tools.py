import random

from ..commons import IEMLObjects, IEMLType
from ..syntax import Sentence, SuperSentence, Text, Word, Morpheme
from ..tools import RandomPoolIEMLObjectGenerator, ieml
from ..dictionary import Term

from .paths import path, resolve_ieml_object
from .parser import USLParser
from .usl import Usl


def usl(arg):
    if isinstance(arg, Usl):
        return arg
    if isinstance(arg, IEMLObjects):
        if isinstance(arg, Term):
            return Usl(Word(root=Morpheme([arg])))
        return Usl(arg)
    if isinstance(arg, str):
        return USLParser().parse(arg)

    if isinstance(arg, dict):
        # map path -> Ieml_object
        return Usl(resolve_ieml_object(arg))

    try:
        rules = [(a, b) for a, b in arg]
    except TypeError:
        pass
    else:
        rules = [(path(a), ieml(b)) for a, b in rules]
        return Usl(resolve_ieml_object(rules))

    raise ValueError("Invalid argument to create an usl object.")

_ieml_objects_types = [Term, Word, Sentence, SuperSentence]
_ieml_object_generator = None

def random_usl(rank_type=None):
    global _ieml_object_generator
    if _ieml_object_generator is None:
        _ieml_object_generator = RandomPoolIEMLObjectGenerator(level=Text)

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


def replace_paths(u, rules):
    k = [(p,t) for p, t in {
            **usl(u).paths,
            **{path(p): ieml(t) for p, t in rules.items()}}.items()]
    return usl(k)
