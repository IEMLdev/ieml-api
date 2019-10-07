from typing import List

import itertools

import bidict

from ieml.constants import MORPHEMES_GRAMMATICAL_MARKERS
from ieml.dictionary.script import Script, script
from ieml.usl import USL
from ieml.usl.polymorpheme import PolyMorpheme, check_polymorpheme


ONE_ACTANT_PROCESS = script('E:S:.')
TWO_ACTANTS_PROCESS = script('E:B:.')
THREE_ACTANTS_PROCESS = script('E:T:.')


INITIATOR_SCRIPT = script('E:.n.-')
INTERACTANT_SCRIPT = script('E:.d.-')
RECIPIENT_SCRIPT = script('E:.k.-')

WHEN_SCRIPT = script('E:.t.-')
WHERE_SCRIPT = script('E:.l.-')
HOW_SCRIPT = script('E:.f.-')
CAUSE_SCRIPT = script('E:.s.-')
INTENTION_SCRIPT = script('E:.m.-')

INDEPENDANT_QUALITY = script('E:U:.')
DEPENDANT_QUALITY = script('E:A:.')


SCRIPTS_ADDRESS_PROCESS = [ONE_ACTANT_PROCESS, TWO_ACTANTS_PROCESS, THREE_ACTANTS_PROCESS]  # process

SCRIPTS_ADDRESS_ACTANTS = [INITIATOR_SCRIPT,  #
                           RECIPIENT_SCRIPT,  # actant destinataire (3eme actant)
                           INTERACTANT_SCRIPT,  # actant intentionnel ou final

                           CAUSE_SCRIPT,  #  actant causal ou instrumental
                           INTENTION_SCRIPT,  # interactant (2eme actant)
                           HOW_SCRIPT,  # actant de manière
                           WHEN_SCRIPT,  # actant temporel
                           WHERE_SCRIPT, ]  # actant spatial


SCRIPTS_ADDRESS_QUALITY = [INDEPENDANT_QUALITY,  # qualité (propriété d'un actant)
                           DEPENDANT_QUALITY]  # actant subordonné (propriété d'un actant)

SCRIPTS_ADDRESS = [*SCRIPTS_ADDRESS_PROCESS, *SCRIPTS_ADDRESS_ACTANTS, *SCRIPTS_ADDRESS_QUALITY]


TYPES_OF_WORDS = [script('E:.b.E:S:.-'), #mot de process
                  script('E:.b.E:B:.-'), #mot d'actant
                  script('E:.b.E:T:.-')] #mot de qualité

NAMES_TO_ADDRESS = {
    ONE_ACTANT_PROCESS: 'process',
    TWO_ACTANTS_PROCESS: 'process',
    THREE_ACTANTS_PROCESS: 'process',

    INITIATOR_SCRIPT: 'initiator',
    INTERACTANT_SCRIPT: 'interactant',
    RECIPIENT_SCRIPT: 'receiver',

    WHEN_SCRIPT: 'when',
    WHERE_SCRIPT: 'where',
    HOW_SCRIPT: 'how',
    INTENTION_SCRIPT: 'intention',
    CAUSE_SCRIPT: 'cause',

    INDEPENDANT_QUALITY: 'independant',
    DEPENDANT_QUALITY: 'dependant'
}

NAMES_ORDERING = {
    'process': 0,

    'initiator': 0,
    'interactant': 0,
    'receiver': 0,

    'when': 0,
    'where': 0,
    'how': 0,
    'intention': 0,
    'cause': 0,

    'independant': 2,
    'dependant': 1
}


def check_address(address):
    assert address.is_singular
    assert all(s in SCRIPTS_ADDRESS for s in address.constant)
    if any(s in SCRIPTS_ADDRESS_PROCESS for s in address.constant):
        assert len(address.constant) == 1
    elif any(s in SCRIPTS_ADDRESS_ACTANTS for s in address.constant):
        assert sum(1 if s in SCRIPTS_ADDRESS_ACTANTS else 0 for s in address.constant) == 1
        assert all(s in SCRIPTS_ADDRESS_QUALITY for s in address.constant
                   if not s in SCRIPTS_ADDRESS_ACTANTS)

    if any(s in SCRIPTS_ADDRESS_QUALITY for s in address.constant):
        assert sum(1 if s == script('E:U:.') else 0 for s in address.constant) <= 1


def check_word(c):
    assert (c.is_empty and len(c.functions) == 0 and c.content.empty and c.klass.empty) or not c.empty, \
        "Empty character must have the E: grammatical class, an empty content and no functions."
    assert (c.contents and not all(pm.empty for pm in c.contents)) or (len(c.functions) != 0 and c.content.empty), \
        "An empty content cannot have a function"
    assert all(isinstance(t, PolyMorpheme) for t in c.poly_morphemes), "A character must be made of Trait"
    assert isinstance(c.klass, Script), "A character must indicate its class with a morpheme from [{}]"\
        .format(', '.join(MORPHEMES_GRAMMATICAL_MARKERS))

    for cc in c.contents:
        check_polymorpheme(cc)
    for f in c.functions:
        for pm in f:
            check_polymorpheme(pm)




def class_from_address(address):
    if any(s in SCRIPTS_ADDRESS_PROCESS for s in address.constant):
        return script('E:.b.E:S:.-')
    elif any(s in SCRIPTS_ADDRESS_ACTANTS for s in address.constant):
        return script('E:.b.E:T:.-')
    else:
        return script('E:.b.E:B:.-')


class Lexeme(USL):
    """A lexeme without the PA of the position on the tree (position independant lexeme)"""
    def __init__(self, pm_address: PolyMorpheme, pm_content: PolyMorpheme=None, pm_transformation: PolyMorpheme=None):
        super().__init__()
        self.pm_address = pm_address
        self.pm_content = pm_content
        self.pm_transformation = pm_transformation
        self.address = PolyMorpheme(constant=[m for m in pm_address.constant if m in SCRIPTS_ADDRESS])
        self.grammatical_class = class_from_address(self.address)
        assert self.pm_address

        self._str = ""
        for pm in [self.pm_address, self.pm_content, self.pm_transformation]:
            if pm is None:
                break
            self._str += "({})".format(str(pm))
        assert self._str

    def __lt__(self, other):
        return self.address < other.address or (self.address == other.address and
               (self.pm_address < other.pm_address or
               (self.pm_address == other.pm_address and self.pm_content and other.pm_content and self.pm_content < other.pm_content) or
               (self.pm_address == other.pm_address and self.pm_content == other.pm_content and
                self.pm_transformation and other.pm_transformation and self.pm_transformation < other.pm_transformation)))

    def _compute_singular_sequences(self):
        if self.pm_address.is_singular and (self.pm_content is None or self.pm_content.is_singular) and \
                (self.pm_transformation is None or self.pm_transformation.is_singular):
            return [self]
        else:
            _product = [self.pm_address,
                        self.pm_content,
                        self.pm_transformation]
            _product = [p.singular_sequences for p in _product if p is not None]

            return [Lexeme(*ss)
                    for ss in itertools.product(*_product)]

    def append_address(self, position: List[Script]):
        pm_address = PolyMorpheme(constant=list(self.pm_address.constant) + position, groups=self.pm_address.groups)
        return Lexeme(pm_address=pm_address,
                      pm_content=self.pm_content,
                      pm_transformation=self.pm_transformation)


class ActantProperties:
    def __init__(self, actant: Lexeme, dependant: 'ActantProperties' = None, independant: List[Lexeme] = None):
        self.actant = actant
        self.dependant = dependant
        self.independant = independant

    def build_positioned_lexemes(self, position: List[Script]):
        res = []
        res.append(self.actant.append_address(position))
        if self.independant:
            res.extend([p.append_address(position + [script('E:U:.')])
                    for p in self.independant])
        if self.dependant:
            res.extend(self.dependant.build_positioned_lexemes(position + [script('E:A:.')]))

        return res

    @staticmethod
    def build_actant_properties(lexemes: List[Lexeme], address_script: Script):
        # address_script = script('E:.n.-')

        children = []
        for l in lexemes:
            if address_script in l.address.constant:
                cst = list(l.pm_address.constant)
                cst.remove(address_script)
                children.append(Lexeme(pm_address=PolyMorpheme(constant=cst,
                                                     groups=l.pm_address.groups),
                                       pm_content=l.pm_content,
                                       pm_transformation=l.pm_transformation),)

        if children:
            actant = [l for l in children if len(l.address.constant) == 0]
            if actant:
                dependants = [l for l in children if DEPENDANT_QUALITY in l.address.constant]

                independants = [Lexeme(pm_address=PolyMorpheme(constant=list(set(l.pm_address.constant) - {INDEPENDANT_QUALITY}),
                                                               groups=l.pm_address.groups),
                                       pm_content=l.pm_content,
                                       pm_transformation=l.pm_transformation)
                            for l in children if INDEPENDANT_QUALITY in l.address.constant and l not in dependants]

                return ActantProperties(actant=actant[0],
                                        dependant=ActantProperties.build_actant_properties(dependants, DEPENDANT_QUALITY),
                                        independant=independants)
        else:
            return None



class SyntagmaticFunction:
    """[<morpheme_klass> trait_content trait_function0 trait_function1]"""

    def __init__(self,
                 process: Lexeme,

                 initiator: ActantProperties=None,
                 interactant: ActantProperties=None,
                 recipient: ActantProperties=None,

                 when: ActantProperties=None,
                 where: ActantProperties=None,
                 intention: ActantProperties=None,
                 how: ActantProperties=None,
                 cause: ActantProperties=None
                 ):
        super().__init__()

        self.process = process

        self.initiator = initiator
        self.interactant = interactant
        self.recipient = recipient

        self.when = when
        self.where = where
        self.how = how
        self.cause = cause
        self.intention = intention

        self.lexemes = self.build_positioned_lexemes()

    @staticmethod
    def from_positioned_lexemes(lexemes: List[Lexeme]):

        process = [l for l in lexemes if set(SCRIPTS_ADDRESS_PROCESS).intersection(l.address.constant)]
        if process:
            process = Lexeme(pm_address=PolyMorpheme(constant=list(set(process[0].pm_address.constant)
                                                                   - set(SCRIPTS_ADDRESS_PROCESS)),
                                                               groups=process[0].pm_address.groups),
                                       pm_content=process[0].pm_content,
                                       pm_transformation=process[0].pm_transformation)
        else:
            process = None

        # build tree
        initiator = ActantProperties.build_actant_properties(lexemes, INITIATOR_SCRIPT)
        interactant = ActantProperties.build_actant_properties(lexemes, INTERACTANT_SCRIPT)
        recipient = ActantProperties.build_actant_properties(lexemes, RECIPIENT_SCRIPT)

        when = ActantProperties.build_actant_properties(lexemes, WHEN_SCRIPT)
        where = ActantProperties.build_actant_properties(lexemes, WHERE_SCRIPT)
        how = ActantProperties.build_actant_properties(lexemes, HOW_SCRIPT)
        cause = ActantProperties.build_actant_properties(lexemes, CAUSE_SCRIPT)
        intention = ActantProperties.build_actant_properties(lexemes, INTENTION_SCRIPT)

        return SyntagmaticFunction(process=process,
                                   initiator=initiator, interactant=interactant, recipient=recipient,
                                   when=when, where=where, how=how, cause=cause, intention=intention)

    def build_positioned_lexemes(self):
        # first determine the type, depending on the positionned lexeme selected
        #
        res = []

        if self.initiator:
            res.extend(self.initiator.build_positioned_lexemes(INITIATOR_SCRIPT))
        i = 1

        if self.interactant:
            res.extend(self.interactant.build_positioned_lexemes([INTERACTANT_SCRIPT]))
            i+=1
        if self.recipient:
            res.extend(self.recipient.build_positioned_lexemes([RECIPIENT_SCRIPT]))
            i+=1

        res.append(self.process.append_address([SCRIPTS_ADDRESS_PROCESS[i]]))

        if self.when:
            res.extend(self.when.build_positioned_lexemes([WHEN_SCRIPT]))

        if self.where:
            res.extend(self.where.build_positioned_lexemes([WHERE_SCRIPT]))

        if self.how:
            res.extend(self.how.build_positioned_lexemes([HOW_SCRIPT]))

        if self.cause:
            res.extend(self.cause.build_positioned_lexemes([CAUSE_SCRIPT]))

        if self.intention:
            res.extend(self.intention.build_positioned_lexemes([INTENTION_SCRIPT]))

        return {l.address: l for l in res}

    def render_string(self, address: PolyMorpheme=None):
        return '[{} {}]'.format(str(self.lexemes[address].grammatical_class),
                                " > ".join([('!' if l.address == address else '')
                                         + str(l) for l in sorted(self.lexemes.values())]))


class Word(USL):
    def __init__(self, syntagmatic_fun: SyntagmaticFunction, address: PolyMorpheme):
        super().__init__()
        self.syntagmatic_fun = syntagmatic_fun
        self.address = address

        self._singular_sequences = None
        self._singular_sequences_set = None

        self._str = self.syntagmatic_fun.render_string(address=self.address)

        self.grammatical_class = class_from_address(self.address)

    def _compute_singular_sequences(self):
        return [self]
