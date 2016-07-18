from ieml.AST.usl import HyperText
from ieml.parsing.script.parser import ScriptParser
from ieml.script import Script
from ieml.exceptions import IncompatiblesScriptsLayers
from ieml.script.script import MultiplicativeScript
from ieml.parsing.parser import USLParser

def m(substance, attribute=None, mode=None):
    children = (substance, attribute, mode)
    if all(isinstance(s, (Script, None.__class__)) for s in children):
        return MultiplicativeScript(children=children)
    else:
        raise NotImplemented


def script(arg):
    if isinstance(arg, str):
        s = ScriptParser().parse(arg)
        s.check()
        return s
    elif isinstance(arg, Script):
        if not arg.is_checked():
            arg.check()
        return arg
    else:
        raise NotImplemented

# shorthand
sc = script


def usl(arg):
    if isinstance(arg, str):
        usl = USLParser().parse(arg)
        usl.check()
        return usl
    elif isinstance(arg, HyperText):
        if not arg.is_checked():
            arg.check()
        return arg
    else:
        raise NotImplemented
