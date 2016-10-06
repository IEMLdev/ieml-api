from ieml.ieml_objects.commons import IEMLObjects
from ieml.usl.parser.parser import USLParser
from ieml.usl.usl import Usl


def usl(arg):
    if isinstance(arg, IEMLObjects):
        return Usl(arg)
    if isinstance(arg, str):
        return USLParser().parse(arg)