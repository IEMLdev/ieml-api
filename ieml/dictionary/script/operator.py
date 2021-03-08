from typing import List

from ieml.dictionary.script.parser import ScriptParser
from ieml.dictionary.script import MultiplicativeScript, Script, AdditiveScript
from ieml.dictionary.script import tools
from ieml.dictionary.script.tools import promote


def m(substance, attribute=None, mode=None):
    children = (substance, attribute, mode)
    if all(isinstance(s, (Script, None.__class__)) for s in children):
        return MultiplicativeScript(children=children)
    else:
        raise NotImplemented


def add(scripts: List[Script]):
    layer = max(s.layer for s in scripts)
    _scripts = [promote(s, layer=layer) for s in scripts]
    return AdditiveScript(children=_scripts)


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

