import random

from ieml.grammar.usl import usl, IEMLSyntaxType
from ..grammar import Fact, Theory, Text, Word, Topic
from ieml.tools import ieml
from ..tools import RandomPoolIEMLObjectGenerator

from .paths import path

_ieml_objects_types = [Word, Topic, Fact, Theory]
_ieml_object_generator = None

def random_usl(rank_type=None):
    global _ieml_object_generator
    if _ieml_object_generator is None:
        _ieml_object_generator = RandomPoolIEMLObjectGenerator(level=Text, pool_size=100)

    if rank_type and not isinstance(rank_type, IEMLSyntaxType):
        raise ValueError('The wanted type for the generated usl object must be a IEMLType, here : '
                         '%s'%rank_type.__class__.__name__)

    if not rank_type:
        i = random.randint(0, 10)
        if i < 4:
            rank_type = _ieml_objects_types[i]
        else:
            rank_type = Text

    return usl(_ieml_object_generator.from_type(rank_type))


class RandomUslGenerator:
    def __init__(self, **kwargs):
        self.generator = RandomPoolIEMLObjectGenerator(**kwargs)

    def __call__(self, type):
        return usl(self.generator.from_type(type))


def replace_paths(u, rules):
    k = [(p,t) for p, t in {
            **usl(u).paths,
            **{path(p): ieml(t) for p, t in rules.items()}}.items()]
    return usl(k)
