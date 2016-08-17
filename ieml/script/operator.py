from ieml.script.parser.parser import ScriptParser
from ieml.script.script import MultiplicativeScript, Script


def m(substance, attribute=None, mode=None):
    children = (substance, attribute, mode)
    if all(isinstance(s, (Script, None.__class__)) for s in children):
        return MultiplicativeScript(children=children)
    else:
        raise NotImplemented


def script(arg):
    if isinstance(arg, str):
        s = ScriptParser().parse(arg)
        return s
    elif isinstance(arg, Script):
        return arg
    else:
        raise NotImplemented

# shorthand
sc = script
