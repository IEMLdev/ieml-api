from typing import List

import itertools

import bidict

from ieml.constants import MORPHEMES_GRAMMATICAL_MARKERS
from ieml.dictionary.script import Script, script
from ieml.usl import USL
from ieml.usl.lexeme import Lexeme, ADDRESS_SCRIPTS, ADDRESS_PROCESS_VALENCE_SCRIPTS, ADDRESS_ACTANTS_SCRIPTS, \
    SCRIPTS_ADDRESS_QUALITY, INDEPENDANT_QUALITY, DEPENDANT_QUALITY, INITIATOR_SCRIPT, INTERACTANT_SCRIPT, \
    RECIPIENT_SCRIPT, TIME_SCRIPT, MANNER_SCRIPT, LOCATION_SCRIPT, CAUSE_SCRIPT, INTENTION_SCRIPT, class_from_address
from ieml.usl.polymorpheme import PolyMorpheme, check_polymorpheme



def check_address(address):
    assert address.is_singular
    assert all(s in ADDRESS_SCRIPTS for s in address.constant)
    if any(s in ADDRESS_PROCESS_VALENCE_SCRIPTS for s in address.constant):
        assert len(address.constant) == 1
    elif any(s in ADDRESS_ACTANTS_SCRIPTS for s in address.constant):
        assert sum(1 if s in ADDRESS_ACTANTS_SCRIPTS else 0 for s in address.constant) == 1
        assert all(s in SCRIPTS_ADDRESS_QUALITY for s in address.constant
                   if not s in ADDRESS_ACTANTS_SCRIPTS)

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

                 time: ActantProperties=None,
                 location: ActantProperties=None,
                 intention: ActantProperties=None,
                 manner: ActantProperties=None,
                 cause: ActantProperties=None
                 ):
        super().__init__()

        self.process = process

        self.initiator = initiator
        self.interactant = interactant
        self.recipient = recipient

        self.time = time
        self.location = location
        self.manner = manner
        self.cause = cause
        self.intention = intention


        self.lexemes, self.valence = self.build_positioned_lexemes()

    @staticmethod
    def from_positioned_lexemes(lexemes: List[Lexeme]):

        process = [l for l in lexemes if set(ADDRESS_PROCESS_VALENCE_SCRIPTS).intersection(l.address.constant)]
        if process:
            process = Lexeme(pm_address=PolyMorpheme(constant=list(set(process[0].pm_address.constant)
                                                                   - set(ADDRESS_PROCESS_VALENCE_SCRIPTS)),
                                                     groups=process[0].pm_address.groups),
                                       pm_content=process[0].pm_content,
                                       pm_transformation=process[0].pm_transformation)
        else:
            process = None

        # build tree
        initiator = ActantProperties.build_actant_properties(lexemes, INITIATOR_SCRIPT)
        interactant = ActantProperties.build_actant_properties(lexemes, INTERACTANT_SCRIPT)
        recipient = ActantProperties.build_actant_properties(lexemes, RECIPIENT_SCRIPT)

        time = ActantProperties.build_actant_properties(lexemes, TIME_SCRIPT)
        location = ActantProperties.build_actant_properties(lexemes, LOCATION_SCRIPT )
        manner = ActantProperties.build_actant_properties(lexemes, MANNER_SCRIPT)
        cause = ActantProperties.build_actant_properties(lexemes, CAUSE_SCRIPT)
        intention = ActantProperties.build_actant_properties(lexemes, INTENTION_SCRIPT)

        return SyntagmaticFunction(process=process,
                                   initiator=initiator, interactant=interactant, recipient=recipient,
                                   time=time, location=location, manner=manner, cause=cause, intention=intention)

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

        res.append(self.process.append_address([ADDRESS_PROCESS_VALENCE_SCRIPTS[i]]))

        if self.time:
            res.extend(self.time.build_positioned_lexemes([TIME_SCRIPT]))

        if self.location:
            res.extend(self.location.build_positioned_lexemes([LOCATION_SCRIPT]))

        if self.manner:
            res.extend(self.manner.build_positioned_lexemes([MANNER_SCRIPT]))

        if self.cause:
            res.extend(self.cause.build_positioned_lexemes([CAUSE_SCRIPT]))

        if self.intention:
            res.extend(self.intention.build_positioned_lexemes([INTENTION_SCRIPT]))

        return {l.address: l for l in res}, ADDRESS_PROCESS_VALENCE_SCRIPTS[i]

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
