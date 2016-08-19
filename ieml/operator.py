from ieml.AST.propositions import SuperSentence, Word, Sentence, Morpheme

from ieml.ieml_objects.parser.parser import USLParser
from ieml.object.terms import Term
from ieml.object.usl import HyperText, Text
from ieml.script import Script
from ieml.script.parser import ScriptParser


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
        return usl
    elif isinstance(arg, HyperText):
        if not arg.is_checked():
            arg.check()
        return arg
    elif isinstance(arg, (Word, Sentence, SuperSentence)):
        usl = HyperText(Text([arg]))
        usl.check()
        return usl
    elif isinstance(arg, Text):
        usl = HyperText(arg)
        usl.check()
        return usl
    elif isinstance(arg, Term):
        usl = HyperText(Text([Word(Morpheme([arg]))]))
        usl.check()
        return usl
    else:
        raise NotImplemented
