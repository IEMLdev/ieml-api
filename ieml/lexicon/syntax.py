from string import ascii_uppercase
from typing import List

from ieml.dictionary.script import Script
import drawSvg as draw

class Paradigm:
    def __eq__(self, other):
        return str(self) == str(other)

class SingularSequence:
    pass

class WordParadigm(Paradigm):
    " ([caractère] x [caractère] x [caractère])"
    def __init__(self, substance, attribute, mode):
        self.substance = substance
        self.attribute = attribute
        self.mode = mode

    def __str__(self):
        return '({})'.format("x".join([str(self.substance), str(self.attribute), str(self.mode)]))

class Word(SingularSequence):
    def __init__(self, substance, attribute, mode):
        self.substance = substance
        self.attribute = attribute
        self.mode = mode
    def __str__(self):
        return '({})'.format("*".join([str(self.substance), str(self.attribute), str(self.mode)]))


class TraitParadigm(Paradigm):
    """<<K(morph morph morph) | An(morph morph…) | Bn (morph morph…) | Cn (morph morph…)>>"""
    def __init__(self,
                 is_functional: bool,
                 constant: List[Script],
                 groups: List):
        self.is_functional = is_functional
        self.constant = sorted(constant)
        self.groups = groups

    def __str__(self):
        bracket = "<{}>" if self.is_functional else "<<{}>>"
        constant = 'K({})'.format(' '.join(map(str, self.constant))) \
            if self.constant else ''
        groups = ["{}{}({})".format(ascii_uppercase[i], j, ' '.join(map(str, group)))
                    for i, (j, group) in enumerate(self.groups)]
        # strip for empty
        return bracket.format('{} {}'.format(constant, ' '.join(groups)).strip())


class Trait(SingularSequence):
    """ < morph morph >"""
    def __init__(self, scripts: List[Script]):
        self.scripts = sorted(scripts)

    def __str__(self):
        return '{}'.format(' '.join(map(str, self.scripts)))

    def anaphore_csv(self):

        main_gramatical_class = max([s.script_class for s in self.scripts])
        core = [s for s in self.scripts if s.script_class == main_gramatical_class]
        rest = [s for s in self.scripts if s not in core]





class CharacterParadigm(Paradigm):
    """[<<contenu>> <fonction> <fonction> <fonction>]"""

    def __init__(self, content: TraitParadigm, functions: List[TraitParadigm]):
        self.content = content
        self.functions = functions

    def __str__(self):
        return "[{}]".format(' '.join(map(str, [self.content] + self.functions)))


class Character(SingularSequence):
    """[<<contenu>> <fonction> <fonction> <fonction>]"""

    def __init__(self, content: Trait, functions: List[Trait]):
        self.content = content
        self.functions = functions

    def __str__(self):
        s_content = ["<<{}>>".format(str(self.content))] if self.content else []
        s_functions = ["<{}>".format(str(f)) for f in self.functions]

        return "[{}]".format(" ".join(s_content + s_functions))

