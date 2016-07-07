from ieml.parsing.script.parser import ScriptParser
from ieml.script import Script
from ieml.exceptions import IncompatiblesScriptsLayers
from ieml.script.script import MultiplicativeScript


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
    if isinstance(arg, Script):
        return arg
    else:
        raise NotImplemented

# shorthand
sc = script
