from ieml.dictionary.script.parser import ScriptParser
from ieml.dictionary.script import MultiplicativeScript, Script
from ieml.dictionary.script import tools


def m(substance, attribute=None, mode=None):
    children = (substance, attribute, mode)
    if all(isinstance(s, (Script, None.__class__)) for s in children):
        return MultiplicativeScript(children=children)
    else:
        raise NotImplemented


def script(arg, promote=False, factorize=False):
    if isinstance(arg, str):
        s = ScriptParser().parse(arg)
    elif isinstance(arg, Script):
        s = arg
    else:
        raise ValueError("Unsupported type {} for {}".format(arg.__class__, arg))

    if factorize:
        return tools.factorize(s, promote=promote)

    return s

