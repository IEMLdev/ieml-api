from ieml.dictionary2.script.parser import ScriptParser
from ieml.dictionary2.script import MultiplicativeScript, Script
from ieml.dictionary2.script.tools import factorize


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
        return factorize(arg)
    else:
        try:
            arg = [script(a) for a in arg]
            return factorize(arg)
        except TypeError:
            pass

    raise NotImplemented
