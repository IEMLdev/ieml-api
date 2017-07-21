from .parser import ScriptParser
from .script import MultiplicativeScript, Script
from .tools import factorize


def m(substance, attribute=None, mode=None):
    children = (substance, attribute, mode)
    if all(isinstance(s, (Script, None.__class__)) for s in children):
        return MultiplicativeScript(children=children)
    else:
        raise NotImplemented


def script(arg):
    from ..terms import Term

    if isinstance(arg, str):
        s = ScriptParser().parse(arg)
        return s
    elif isinstance(arg, Script):
        return arg
    elif isinstance(arg, Term):
        return arg.script
    else:
        try:
            arg = [script(a) for a in arg]
            return factorize(arg)
        except TypeError:
            pass

    raise NotImplemented


# shorthand
sc = script
