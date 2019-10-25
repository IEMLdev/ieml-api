from enum import Enum
from itertools import chain, count
from typing import List, Set

from ieml.constants import AUXILIARY_CLASS
from ieml.dictionary.script import script, Script

SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT = script('E:.b.E:S:.-')
SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT = script('E:.b.E:B:.-')
SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT = script('E:.b.E:T:.-')

# Process : grammatical role (valence)
ONE_ACTANT_PROCESS = script('E:S:.')
TWO_ACTANTS_PROCESS = script('E:B:.')
THREE_ACTANTS_PROCESS = script('E:T:.')
ADDRESS_PROCESS_VALENCE_SCRIPTS = [ONE_ACTANT_PROCESS, TWO_ACTANTS_PROCESS, THREE_ACTANTS_PROCESS]  # process



# Process : mandatory address
ADDRESS_PROCESS_VOICES_SCRIPTS = {
    ONE_ACTANT_PROCESS: {script("E:.-wa.-t.o.-'"), # Actif
                         script("E:.-wo.-t.o.-'"),}, # Passif
    TWO_ACTANTS_PROCESS: script("E:.-O:O:.-t.o.-'").singular_sequences_set,
    THREE_ACTANTS_PROCESS: script("E:.-O:O:.-t.o.-'").singular_sequences_set
}
assert all(e in ADDRESS_PROCESS_VOICES_SCRIPTS[THREE_ACTANTS_PROCESS]
           for e in ADDRESS_PROCESS_VOICES_SCRIPTS[ONE_ACTANT_PROCESS])
ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS = script("E:.-'O:O:.-M:.-'t.o.-',").singular_sequences_set

# Process : optional address
ADDRESS_PROCESS_ASPECT_SCRIPTS = script("E:F:.-t.o.-'").singular_sequences_set
ADDRESS_PROCESS_TENSE_SCRIPTS = script("E:M:.-O:.-t.o.-'").singular_sequences_set

ADDRESS_PROCESS_POLYMORPHEME_SCRIPTS = {
    *ADDRESS_PROCESS_VALENCE_SCRIPTS, # valence
    *ADDRESS_PROCESS_VOICES_SCRIPTS[THREE_ACTANTS_PROCESS],  # voix / voice
    *ADDRESS_PROCESS_ASPECT_SCRIPTS,  # aspect
    *ADDRESS_PROCESS_TENSE_SCRIPTS,  # temps / tense
    *ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS,  # mode
}

# Process : optional transformation
TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS = script("E:O:O:.").singular_sequences_set
TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS = script("E:M:O:.").singular_sequences_set
TRANSFORMATION_PROCESS_TETRADE_MODE_SCRIPTS = script("E:.b.O:O:.-").singular_sequences_set
TRANSFORMATION_PROCESS_HEXADE_MODE_SCRIPTS = script("E:.b.O:M:.-").singular_sequences_set

TRANSFORMATION_PROCESS_SCRIPTS = {
    *TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS,
    *TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS,
    *TRANSFORMATION_PROCESS_TETRADE_MODE_SCRIPTS,
    *TRANSFORMATION_PROCESS_HEXADE_MODE_SCRIPTS
}

SYNTAGMATIC_FUNCTION_SCRIPT = script('E:.b.-')



# Actant : grammatical roles
INITIATOR_SCRIPT = script('E:.n.-')
INTERACTANT_SCRIPT = script('E:.d.-')
RECIPIENT_SCRIPT = script('E:.k.-')
ADDRESS_ACTANTS_MOTOR_SCRIPTS = [INITIATOR_SCRIPT, INTERACTANT_SCRIPT, RECIPIENT_SCRIPT]

TIME_SCRIPT = script('E:.t.-')
LOCATION_SCRIPT = script('E:.l.-')
MANNER_SCRIPT = script('E:.f.-')
CAUSE_SCRIPT = script('E:.s.-')
INTENTION_SCRIPT = script('E:.m.-')
ADDRESS_CIRCONSTANTIAL_ACTANTS_SCRIPTS = [TIME_SCRIPT, LOCATION_SCRIPT, MANNER_SCRIPT, CAUSE_SCRIPT, INTENTION_SCRIPT]
ACTANTS_SCRIPTS = [*ADDRESS_ACTANTS_MOTOR_SCRIPTS,
                   *ADDRESS_CIRCONSTANTIAL_ACTANTS_SCRIPTS]


# class ScriptsEnum(Enum):
#     @staticmethod
#     def from_paradigm(cls):
#         return cls( [(i.name, i.value) for i in chain(MotorActants, CirconstantialActants)])
#


class MotorActants(Enum):
    INITIATOR = script('E:.n.-')
    INTERACTANT = script('E:.d.-')
    RECIPIENT = script('E:.k.-')

class CirconstantialActants(Enum):
    TIME = script('E:.t.-')
    LOCATION = script('E:.l.-')
    MANNER = script('E:.f.-')
    CAUSE = script('E:.s.-')
    INTENTION = script('E:.m.-')


Actants = Enum('Actants', [(i.name, i.value) for i in chain(MotorActants, CirconstantialActants)])




INDEPENDANT_QUALITY = script('E:U:.')
DEPENDANT_QUALITY = script('E:A:.')
SCRIPTS_ADDRESS_QUALITY = [DEPENDANT_QUALITY, INDEPENDANT_QUALITY]
ADDRESS_SCRIPTS = [*ADDRESS_PROCESS_VALENCE_SCRIPTS, *ACTANTS_SCRIPTS, *SCRIPTS_ADDRESS_QUALITY]

ADDRESS_SCRIPTS_ORDER = dict(zip(ADDRESS_SCRIPTS, count()))

# Grammatical classes
TYPES_OF_WORDS = [script('E:.b.E:S:.-'), #mot de process
                  script('E:.b.E:B:.-'), #mot d'actant
                  script('E:.b.E:T:.-')] #mot de qualité

NAMES_TO_ADDRESS = {
    ONE_ACTANT_PROCESS: 'process',
    TWO_ACTANTS_PROCESS: 'process',
    THREE_ACTANTS_PROCESS: 'process',

    INITIATOR_SCRIPT: 'initiator',
    INTERACTANT_SCRIPT: 'interactant',
    RECIPIENT_SCRIPT: 'recipient',

    TIME_SCRIPT: 'time',
    LOCATION_SCRIPT: 'location',
    MANNER_SCRIPT: 'manner',
    INTENTION_SCRIPT: 'intention',
    CAUSE_SCRIPT: 'cause',

    INDEPENDANT_QUALITY: 'independant',
    DEPENDANT_QUALITY: 'dependant'
}

ROLE_NAMES_TO_SCRIPT= {
    'initiator': INITIATOR_SCRIPT,
    'interactant': INTERACTANT_SCRIPT,
    'recipient' : RECIPIENT_SCRIPT,

    'time': TIME_SCRIPT,
    'location': LOCATION_SCRIPT,
    'manner': MANNER_SCRIPT,
    'intention': INTENTION_SCRIPT,
    'cause': CAUSE_SCRIPT,

    'independant': INDEPENDANT_QUALITY,
    'dependant': DEPENDANT_QUALITY
}

NAMES_ORDERING = {
    'process': 0,

    'initiator': 0,
    'interactant': 0,
    'recipient': 0,

    'time': 0,
    'location': 0,
    'manner': 0,
    'intention': 0,
    'cause': 0,

    'independant': 2,
    'dependant': 1
}

# Actant : mandatory address
ADDRESS_ACTANTS_DEFINITION_SCRIPTS = script("E:M:.-d.u.-'").singular_sequences_set
ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS = script("E:.O:O:.-").singular_sequences_set

# Actant : optional address
ADDRESS_ACTANTS_CONTINUITY_SCRIPTS = script("E:.-',b.-S:.U:.-'y.-'O:.-',_").singular_sequences_set
ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS = script("E:.-n.E:U:.+F:.-'").singular_sequences_set
ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS = script("E:I:.-t.u.-'").singular_sequences_set

ADDRESS_ACTANT_SCRIPTS = {
    *ACTANTS_SCRIPTS,
    *ADDRESS_ACTANTS_DEFINITION_SCRIPTS,  # definition
    *ADDRESS_ACTANTS_CONTINUITY_SCRIPTS,  # continuity
    *ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS,  # genre / gender
    *ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS,  # nombre / number
    *ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS,  # quantité / quantity
}

ADDRESS_QUALITY_GRADIENT_EMM_SCRIPTS = script("E:M:M:.").singular_sequences_set
ADDRESS_QUALITY_GRADIENT_EFM_SCRIPTS = script("E:F:M:.").singular_sequences_set

GROUPEMENT_SCRIPTS = script("E:S:.j.-'M:O:.-O:.-',").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS = script("E:S:M:.").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS = script("E:B:M:.").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS = script("E:T:M:.").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS = script("E:.-O:.M:M:.-l.-'").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS = script("E:.-M:.M:M:.-l.-'").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS = script("E:.-F:.M:M:.-l.-'").singular_sequences_set

assert {*ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS,
        *ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS} == ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS

ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS = {script("E:T:.p.-"), script("E:.A:.h.-")}

ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS = script("E:.O:.M:O:.-").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_EOM_SCRIPTS = script("E:O:M:.").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS = script("E:M:.d.+M:O:.-").singular_sequences_set


TRANSFORMATION_MOTOR_ACTANT_SCRIPTS = {
    *TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS,
    *TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS,
    *ADDRESS_QUALITY_GRADIENT_EMM_SCRIPTS,
    *ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS,
    *ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS,
    *ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS,
    *GROUPEMENT_SCRIPTS
}

ADDRESS_QUALITY_SCRIPTS = {
    *ACTANTS_SCRIPTS,
    *SCRIPTS_ADDRESS_QUALITY,
    *TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS,  # construction
    *TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS,  # mode
    *ADDRESS_ACTANTS_DEFINITION_SCRIPTS,  # definition
    *ADDRESS_QUALITY_GRADIENT_EFM_SCRIPTS,  # nombre / number
    *ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS,
    *ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS,
    *ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS
}


def assert_(cond, message):
    if not cond:
        raise ValueError(message)


def assert_all_in(l: List[Script], _set: Set[Script], name_l):
    assert_(all(s in _set for s in l),
            "Invalid scripts [{}] in {}. Received: [{}]".format(
                " ".join(map(str, sorted(set(l) - _set))),
                name_l,
                ' '.join(map(str, sorted(l)))))


def assert_only_one_from(l: List[Script], _set: Set[Script], name_l, name_set) -> Script:
    assert_(sum(1 if s in _set else 0 for s in l) == 1,
            "One and only one of the {} scripts [{}] required in {}. Received: [{}]".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l,
                            ' '.join(map(str, sorted(l)))))

    return next(iter(s for s in l if s in _set))


def assert_atmost_one_from(l: List[Script], _set: Set[Script], name_l, name_set):
    assert_(sum(1 if s in _set else 0 for s in l) <= 1,
            "Maximum one of the {} scripts [{}] required in {}. Received: [{}]".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l,
                            ' '.join(map(str, sorted(l)))))


def assert_no_one_from(l: List[Script], _set: Set[Script], name_l, name_set):
    assert_(sum(1 if s in _set else 0 for s in l) == 0,
            "The {} scripts [{}] are forbidden in {}. Received: [{}]".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l,
                            ' '.join(map(str, sorted(l)))))


def get_role_of_pa(l: List[Script]):
    if INDEPENDANT_QUALITY in l:
        return INDEPENDANT_QUALITY

    if DEPENDANT_QUALITY in l:
        return DEPENDANT_QUALITY

    return assert_only_one_from(l, {*ACTANTS_SCRIPTS, *ADDRESS_PROCESS_VALENCE_SCRIPTS}, "an address", "grammatical roles")


def check_address_process_scripts(l: List[Script], valence=None):
    # check all
    assert_all_in(l, ADDRESS_PROCESS_POLYMORPHEME_SCRIPTS, "an address of a process")

    #check valence
    if valence is None:
        valence = assert_only_one_from(l, set(ADDRESS_PROCESS_VALENCE_SCRIPTS), "an address of a process", "valences")

    #check voice
    assert_only_one_from(l, ADDRESS_PROCESS_VOICES_SCRIPTS[valence], "an address of a process", "voices")

    #check mode
    assert_only_one_from(l, ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS, "an address of a process", "verbal modes")

    #check aspect
    assert_atmost_one_from(l, ADDRESS_PROCESS_ASPECT_SCRIPTS, "an address of a process", "aspects")

    #check tense
    assert_atmost_one_from(l, ADDRESS_PROCESS_TENSE_SCRIPTS, "an address of a process", "tenses")


def check_transformation_process_scripts(l: List[Script]):
    assert_all_in(l, TRANSFORMATION_PROCESS_SCRIPTS, "a transformation of a process")

    # check logical constructions
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS, "a transformation of a process", "logical constructions")

    # check logical modes
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS, "a transformation of a process", "logical modes")

    # check tetrade modes
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_TETRADE_MODE_SCRIPTS, "a transformation of a process", "tetrade modes")

    # check hexade modes
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_HEXADE_MODE_SCRIPTS, "a transformation of a process", "hexade modes")


def check_address_script(l: List[Script]):
    assert_all_in(l, set(ADDRESS_SCRIPTS), "an address")

    if any(e in {*ADDRESS_PROCESS_VALENCE_SCRIPTS, *ACTANTS_SCRIPTS} for e in l):
        assert_only_one_from(l, {*ADDRESS_PROCESS_VALENCE_SCRIPTS, *ACTANTS_SCRIPTS}, "an address", "grammatical roles")

    assert_atmost_one_from(l, {INDEPENDANT_QUALITY}, "an address", "independant quality")


def check_address_actant_scripts(l: List[Script], role=None):
    assert_all_in(l, {DEPENDANT_QUALITY, *ADDRESS_ACTANT_SCRIPTS}, "an address of an actant")

    if role is None:
        role = assert_only_one_from(l, set(ACTANTS_SCRIPTS), "an address of an actant", "grammatical roles")
        # assert_atmost_one_from(l, {INDEPENDANT_QUALITY}, "an address of an actant", "dependant")

    assert_only_one_from(l, ADDRESS_ACTANTS_DEFINITION_SCRIPTS, "an address of an actant", "definitions")

    assert_only_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS, "an address of an actant", "grammatical numbers")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_CONTINUITY_SCRIPTS, "an address of an actant", "continuities")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS, "an address of an actant", "grammatical genders")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS, "an address of an actant", "quantifications")


def check_transformation_actant_scripts(l: List[Script]):
    assert_(all(s.grammatical_class == AUXILIARY_CLASS for s in l),
            "The script must be auxiliary in a transformation of an actant [{}]".format(
                ' '.join(map(str, sorted(s for s in l if s.grammatical_class != AUXILIARY_CLASS)))))

    assert_no_one_from(l, ADDRESS_PROCESS_ASPECT_SCRIPTS, "a transformation of an actant", "aspects")
    assert_no_one_from(l, ADDRESS_PROCESS_TENSE_SCRIPTS, "a transformation of an actant", "tenses")
    assert_no_one_from(l, ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS, "a transformation of an actant", "verbal modes")
    assert_no_one_from(l, ADDRESS_PROCESS_VOICES_SCRIPTS[THREE_ACTANTS_PROCESS], "a transformation of an actant", "voices")

    assert_no_one_from(l, TRANSFORMATION_PROCESS_TETRADE_MODE_SCRIPTS, "a transformation of an actant", "tetrade modes")
    assert_no_one_from(l, TRANSFORMATION_PROCESS_HEXADE_MODE_SCRIPTS, "a transformation of an actant", "hexade modes")

    assert_no_one_from(l, ADDRESS_ACTANTS_DEFINITION_SCRIPTS, "a transformation of an actant", "definitions")
    assert_no_one_from(l, ADDRESS_ACTANTS_CONTINUITY_SCRIPTS, "a transformation of an actant", "continuities")
    assert_no_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS, "a transformation of an actant", "grammatical genders")
    assert_no_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS, "a transformation of an actant", "grammatical numbers")
    assert_no_one_from(l, ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS, "a transformation of an actant", "quantifications")

    assert_no_one_from(l, ADDRESS_QUALITY_GRADIENT_EMM_SCRIPTS, "a transformation of an actant", "gradients")

    assert_no_one_from(l, set(ADDRESS_SCRIPTS), "a transformation of an actant", "grammatical roles")


def check_address_motor_actant_scripts(l: List[Script], role=None):
    if role is None:
        assert_only_one_from(l, set(ADDRESS_ACTANTS_MOTOR_SCRIPTS), "an address of a motor actant", "motor grammaticals roles")

    check_address_actant_scripts(l, role=role)


def check_transformation_motor_actant_scripts(l: List[Script]):
    assert_all_in(l, TRANSFORMATION_MOTOR_ACTANT_SCRIPTS, "a transformation of a motor actant")

    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS, "a transformation of a motor actant",
                         "logical constructions")
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS, "a transformation of a motor actant",
                         "logical modes")
    assert_atmost_one_from(l, ADDRESS_QUALITY_GRADIENT_EMM_SCRIPTS, "a transformation of a motor actant",
                         "gradients")
    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS, "a transformation of a motor actant",
                         "manners")
    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS, "a transformation of a motor actant",
                         "causes")
    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS, "a transformation of a motor actant",
                         "spacial relationships")
    assert_atmost_one_from(l, GROUPEMENT_SCRIPTS, "a transformation of a motor actant",
                         "groupements")


def check_address_circonstancial_actant_scripts(l: List[Script], role=None):
    if role is None:
        role = assert_only_one_from(l, set(ADDRESS_CIRCONSTANTIAL_ACTANTS_SCRIPTS), "an address of a circonstantial actant",
                                    "grammatical roles")
        assert_atmost_one_from(l, {INDEPENDANT_QUALITY}, "an address of an actant", "dependant")

    assert_only_one_from(l, ADDRESS_ACTANTS_DEFINITION_SCRIPTS, "an address of an actant", "definitions")

    assert_only_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS, "an address of an actant", "grammatical numbers")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_CONTINUITY_SCRIPTS, "an address of an actant", "continuities")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS, "an address of an actant", "grammatical genders")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS, "an address of an actant", "quantifications")

    if role == TIME_SCRIPT:
        assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS, "an address of a time actant",
                               "time distributions")
        assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS, "an address of a time actant",
                               "frequency distributions")
        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS},
                      "an address of a time actant")

    elif role == LOCATION_SCRIPT:
        assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS, "an address of a space actant",
                               "space distributions")
        assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS, "an address of a space actant",
                               "axial orientation")
        assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS,
                               "an address of a space actant",
                               "path orientation")

        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS},
                      "an address of a space actant")

    elif role == INTENTION_SCRIPT:
        assert_atmost_one_from(l, set(ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS),
                                    "an address of a intention actant",
                                    "type of motivation")

        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS},
                      "an address of a intention actant")

    elif role == MANNER_SCRIPT:
        assert_atmost_one_from(l, set(ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS),
                                    "an address of a manner actant",
                                    "manner")
        assert_atmost_one_from(l, set(ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_EOM_SCRIPTS),
                                    "an address of a manner actant",
                                    "gradient adverbs")
        assert_atmost_one_from(l, set(GROUPEMENT_SCRIPTS),
                                    "an address of a manner actant",
                                    "groupements")
        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_EOM_SCRIPTS,
                          *GROUPEMENT_SCRIPTS},
                      "an address of a manner actant")

    elif role == CAUSE_SCRIPT:
        assert_atmost_one_from(l, set(ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS),
                                    "an address of a cause actant",
                                    "causes")
        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS},
                      "an address of a cause actant")

    return role


def check_transformation_circonstancial_actant_scripts(l: List[Script], role: Script):
    check_transformation_actant_scripts(l)

    if role == TIME_SCRIPT:
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS, "a transformation of a time actant",
                           "time distributions")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS, "a transformation of a time actant",
                           "frequency distributions")

    elif role == LOCATION_SCRIPT:
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS, "a transformation of a location actant",
                               "space distributions")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS, "a transformation of a location actant",
                               "axial orientation")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS,
                               "a transformation of a location actant",
                               "path orientation")

    elif role == INTENTION_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS),
                             "a transformation of a intention actant",
                             "type of motivation")

    elif role == MANNER_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS),
                                    "a transformation of a manner actant",
                                    "manner")
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_EOM_SCRIPTS),
                                    "a transformation of a manner actant",
                                    "gradient adverbs")
        assert_no_one_from(l, set(GROUPEMENT_SCRIPTS),
                                    "a transformation of a manner actant",
                                    "groupements")

    elif role == CAUSE_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS),
                                    "a transformation of a cause actant",
                                    "causes")


def check_address_quality(l: List[Script], role=None):
    assert_all_in(l, ADDRESS_QUALITY_SCRIPTS, "an address of a quality")

    if role is None:
        assert_only_one_from(l, set(ACTANTS_SCRIPTS), "an address of an actant", "grammatical roles")
        assert_only_one_from(l, {INDEPENDANT_QUALITY}, "an address of an actant", "dependant")

    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS, "an address of an actant",
                           "logical constructions")
    assert_atmost_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS, "an address of an actant", "logical modes")
    assert_atmost_one_from(l, ADDRESS_ACTANTS_DEFINITION_SCRIPTS, "an address of an actant", "definitions")

    assert_atmost_one_from(l, ADDRESS_QUALITY_GRADIENT_EFM_SCRIPTS, "an address of an actant", "gradients")

    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS, "an address of an actant", "manners")

    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS, "an address of an actant", "causals")

    assert_atmost_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_SCRIPTS, "an address of an actant", "locations")


def check_transformation_quality(l: List[Script]):
    assert_(len(l) == 0, "A quality can't have a transformation polymorpheme.")


def check_lexeme_scripts(l_pa: List[Script], l_pc: List[Script], l_pt: List[Script], role=None):
    # if role is None:
    #     _role = get_role_of_pa(l_pa)
    # else:
    if len(role) != 1:
        raise ValueError("Invalid role : {}".format(' '.join(map(str, role))))
    _role = role[0]

    if _role in ADDRESS_PROCESS_VALENCE_SCRIPTS:
        check_address_process_scripts(l_pa, valence=_role)
        check_transformation_process_scripts(l_pt)
    elif _role in ADDRESS_ACTANTS_MOTOR_SCRIPTS:
        check_address_motor_actant_scripts(l_pa, role=_role)
        check_transformation_motor_actant_scripts(l_pt)
    elif _role in ADDRESS_CIRCONSTANTIAL_ACTANTS_SCRIPTS:
        circ_role = check_address_circonstancial_actant_scripts(l_pa, role=_role)
        check_transformation_circonstancial_actant_scripts(l_pt, role=circ_role)
    elif _role == DEPENDANT_QUALITY:
        check_address_actant_scripts(l_pa, role=_role)
        check_transformation_actant_scripts(l_pt)
    elif _role == INDEPENDANT_QUALITY:
        check_address_quality(l_pa, role=_role)
        check_transformation_quality(l_pt)
    else:
        raise ValueError("Invalid role: {}".format(str(_role)))
