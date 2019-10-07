from typing import List, Set

from ieml.constants import AUXILIARY_CLASS
from ieml.dictionary.script import script, Script




def assert_(cond, message):
    if not cond:
        raise ValueError(message)


def assert_all_in(l: List[Script], _set: Set[Script], name_l):
    assert_(all(s in _set for s in l),
            "Invalid scripts [{}] in {}".format(
                " ".join(map(str, sorted(set(l) - _set))),
                name_l))

def assert_only_one_from(l: List[Script], _set: Set[Script], name_l, name_set) -> Script:
    assert_(sum(1 if s in _set else 0 for s in l) == 1,
            "One and only one of {} scripts [{}] required in {}".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l))

    return next(iter(s for s in l if s in _set))

def assert_atmost_one_from(l: List[Script], _set: Set[Script], name_l, name_set):
    assert_(sum(1 if s in _set else 0 for s in l) <= 1,
            "Only one of {} scripts [{}] required in {}".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l))


def assert_no_one_from(l: List[Script], _set: Set[Script], name_l, name_set):
    assert_(sum(1 if s in _set else 0 for s in l) == 0,
            "The {} scripts [{}] are forbidden in {}".format(
                            name_set,
                            ' '.join(map(str, sorted(_set))),
                            name_l))



ONE_ACTANT_PROCESS = script('E:S:.')
TWO_ACTANTS_PROCESS = script('E:B:.')
THREE_ACTANTS_PROCESS = script('E:T:.')
ADDRESS_PROCESS_VALENCE_SCRIPTS = [ONE_ACTANT_PROCESS, TWO_ACTANTS_PROCESS, THREE_ACTANTS_PROCESS]  # process

ADDRESS_PROCESS_VOICES_SCRIPTS = {
    ONE_ACTANT_PROCESS: {script("E:.-wa.-t.o.-'"), # Actif
                         script("E:.-wo.-t.o.-'"),}, # Passif
    TWO_ACTANTS_PROCESS: script("E:.-O:O:.-t.o.-'").singular_sequences_set,
    THREE_ACTANTS_PROCESS: script("E:.-O:O:.-t.o.-'").singular_sequences_set
}
assert all(e in ADDRESS_PROCESS_VOICES_SCRIPTS[THREE_ACTANTS_PROCESS]
           for e in ADDRESS_PROCESS_VOICES_SCRIPTS[ONE_ACTANT_PROCESS])

ADDRESS_PROCESS_ASPECT_SCRIPTS = script("E:F:.-t.o.-'").singular_sequences_set
ADDRESS_PROCESS_TENSE_SCRIPTS = script("E:M:.-O:.-t.o.-'").singular_sequences_set
ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS = script("E:.-'O:O:.-M:.-'t.o.-',").singular_sequences_set

ADDRESS_PROCESS_POLYMORPHEME_SCRIPTS = {
    *ADDRESS_PROCESS_VALENCE_SCRIPTS, # valence
    *ADDRESS_PROCESS_VOICES_SCRIPTS[THREE_ACTANTS_PROCESS],  # voix / voice
    *ADDRESS_PROCESS_ASPECT_SCRIPTS,  # aspect
    *ADDRESS_PROCESS_TENSE_SCRIPTS,  # temps / tense
    *ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS,  # mode
}


def check_address_process_scripts(l: List[Script]):
    # check all
    assert_all_in(l, ADDRESS_PROCESS_POLYMORPHEME_SCRIPTS, "an address of a process")

    #check valence
    valence = assert_only_one_from(l, set(ADDRESS_PROCESS_VALENCE_SCRIPTS), "an address of a process", "valences")

    #check voice
    assert_only_one_from(l, ADDRESS_PROCESS_VOICES_SCRIPTS[valence], "an address of a process", "voices")

    #check mode
    assert_only_one_from(l, ADDRESS_PROCESS_VERBAL_MODE_SCRIPTS, "an address of a process", "verbal modes")

    #check aspect
    assert_atmost_one_from(l, ADDRESS_PROCESS_ASPECT_SCRIPTS, "an address of a process", "aspects")

    #check tense
    assert_atmost_one_from(l, ADDRESS_PROCESS_TENSE_SCRIPTS, "an address of a process", "tenses")


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

INDEPENDANT_QUALITY = script('E:U:.')
DEPENDANT_QUALITY = script('E:A:.')


ADDRESS_ACTANTS_SCRIPTS = [*ADDRESS_ACTANTS_MOTOR_SCRIPTS,
                            *ADDRESS_CIRCONSTANTIAL_ACTANTS_SCRIPTS]


SCRIPTS_ADDRESS_QUALITY = [INDEPENDANT_QUALITY,  # qualité (propriété d'un actant)
                           DEPENDANT_QUALITY]  # actant subordonné (propriété d'un actant)



ADDRESS_SCRIPTS = [*ADDRESS_PROCESS_VALENCE_SCRIPTS, *ADDRESS_ACTANTS_SCRIPTS, *SCRIPTS_ADDRESS_QUALITY]


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

    TIME_SCRIPT: 'time',
    LOCATION_SCRIPT: 'location',
    MANNER_SCRIPT: 'manner',
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

ADDRESS_ACTANTS_DEFINITION_SCRIPTS = script("E:M:.-d.u.-'").singular_sequences_set
ADDRESS_ACTANTS_CONTINUITY_SCRIPTS = script("E:.-',b.-S:.U:.-'y.-'O:.-',_").singular_sequences_set
ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS = script("E:.-n.E:U:.+F:.-'").singular_sequences_set
ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS = script("E:.O:O:.-").singular_sequences_set
ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS = script("E:I:.-t.u.-'").singular_sequences_set

ADDRESS_ACTANT_SCRIPTS = {
    *ADDRESS_ACTANTS_SCRIPTS
    *ADDRESS_ACTANTS_DEFINITION_SCRIPTS,  # definition
    *ADDRESS_ACTANTS_CONTINUITY_SCRIPTS,  # continuity
    *ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS,  # genre / gender
    *ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS,  # nombre / number
    *ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS,  # quantité / quantity
}

ADDRESS_QUALITY_GRADIENT_SCRIPTS = script("E:M:M:.").singular_sequences_set
GROUPEMENT_SCRIPTS = script("E:S:.j.-'M:O:.-O:.-',").singular_sequences_set

def check_address_actant_scripts(l: List[Script]):
    assert_all_in(l, ADDRESS_ACTANT_SCRIPTS, "an address of an actant")

    role = assert_only_one_from(l, set(ADDRESS_ACTANTS_SCRIPTS), "an address of an actant", "grammatical roles")
    assert_atmost_one_from(l, {INDEPENDANT_QUALITY}, "an address of an actant", "dependant")

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

    assert_no_one_from(l, ADDRESS_QUALITY_GRADIENT_SCRIPTS, "a transformation of an actant", "gradients")

    assert_no_one_from(l, set(ADDRESS_SCRIPTS), "a transformation of an actant", "grammatical roles")



def check_address_motor_actant_scripts(l: List[Script]):
    assert_only_one_from(l, set(ADDRESS_ACTANTS_MOTOR_SCRIPTS), "an address of a motor actant", "motor grammaticals roles")
    check_address_actant_scripts(l)


TRANSFORMATION_MOTOR_ACTANT_SCRIPTS = {
    *TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS,
    *TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS,
    *ADDRESS_QUALITY_GRADIENT_SCRIPTS,
    *ADDRESS_MANNER_SCRIPTS,
    *ADDRESS_CAUSE_SCRIPTS,
    *ADDRESS_LOCATION_SCRIPTS,
    *GROUPEMENT_SCRIPTS
}

def check_transformation_motor_actant_scripts(l: List[Script]):
    assert_all_in(l, TRANSFORMATION_MOTOR_ACTANT_SCRIPTS, "a transformation of a motor actant")

    assert_only_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_CONSTRUCTION_SCRIPTS, "a transformation of a motor actant",
                         "logical constructions")
    assert_only_one_from(l, TRANSFORMATION_PROCESS_LOGICAL_MODE_SCRIPTS, "a transformation of a motor actant",
                         "logical modes")
    assert_only_one_from(l, ADDRESS_QUALITY_GRADIENT_SCRIPTS, "a transformation of a motor actant",
                         "gradients")
    assert_only_one_from(l, ADDRESS_MANNER_SCRIPTS, "a transformation of a motor actant",
                         "manners")
    assert_only_one_from(l, ADDRESS_CAUSE_SCRIPTS, "a transformation of a motor actant",
                         "causes")
    assert_only_one_from(l, ADDRESS_LOCATION_SCRIPTS, "a transformation of a motor actant",
                         "spacial relationships")
    assert_only_one_from(l, GROUPEMENT_SCRIPTS, "a transformation of a motor actant",
                         "groupements")


ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS = script("E:S:M:.").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS = script("E:B:M:.").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS = script("E:T:M:.").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS = script("E:.-O:.M:M:.-l.-'").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS = script("E:.-M:.M:M:.-l.-'").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS = {script("E:T:.p.-"), script("E:.A:.h.-")}

ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS = script("E:.O:.M:O:.-").singular_sequences_set
ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_SCRIPTS = script("E:O:M:.").singular_sequences_set

ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS = script("E:M:.d.+M:O:.-").singular_sequences_set


def check_address_circonstancial_actant_scripts(l: List[Script]):
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
        assert_only_one_from(l, set(ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS),
                                    "an address of a intention actant",
                                    "type of motivation")

        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS},
                      "an address of a intention actant")

    elif role == MANNER_SCRIPT:
        assert_only_one_from(l, set(ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS),
                                    "an address of a manner actant",
                                    "manner")
        assert_only_one_from(l, set(ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_SCRIPTS),
                                    "an address of a manner actant",
                                    "gradient adverbs")
        assert_only_one_from(l, set(GROUPEMENT_SCRIPTS),
                                    "an address of a manner actant",
                                    "groupements")
        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_SCRIPTS,
                          *GROUPEMENT_SCRIPTS},
                      "an address of a manner actant")

    elif role == CAUSE_SCRIPT:
        assert_only_one_from(l, set(ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS),
                                    "an address of a cause actant",
                                    "cause")
        assert_all_in(l, {*ADDRESS_ACTANT_SCRIPTS,
                          *ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS},
                      "an address of a cause actant")


def check_transformation_circonstancial_actant_scripts(l: List[Script], role: Script):
    check_transformation_actant_scripts(l)

    if role == TIME_SCRIPT:
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_TIME_DISTRIBUTION_SCRIPTS, "a transformation of a time actant",
                           "time distributions")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_FREQUENCY_DISTRIBUTION_SCRIPTS, "a transformation of a time actant",
                           "frequency distributions")

    elif role == LOCATION_SCRIPT:
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_SPACE_DISTRIBUTION_SCRIPTS, "an address of a location actant",
                               "space distributions")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_TOWARDS_AXES_SCRIPTS, "an address of a location actant",
                               "axial orientation")
        assert_no_one_from(l, ADDRESS_CIRCONSTANTIAL_LOCATION_PATH_SCRIPTS,
                               "an address of a location actant",
                               "path orientation")

    elif role == INTENTION_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_INTENTION_SCRIPTS),
                             "an address of a intention actant",
                             "type of motivation")

    elif role == MANNER_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_MANNER_SCRIPTS),
                                    "an address of a manner actant",
                                    "manner")
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_GRADIENT_ADVERB_SCRIPTS),
                                    "an address of a manner actant",
                                    "gradient adverbs")
        assert_no_one_from(l, set(GROUPEMENT_SCRIPTS),
                                    "an address of a manner actant",
                                    "groupements")

    elif role == CAUSE_SCRIPT:
        assert_no_one_from(l, set(ADDRESS_CIRCONSTANTIAL_CAUSE_SCRIPTS),
                                    "an address of a cause actant",
                                    "cause")


def check_address_quality(l: List[Script]):
    assert_all_in(l, ADDRESS_ACTANT_SCRIPTS, "an address of an actant")

    role = assert_only_one_from(l, set(ADDRESS_ACTANTS_SCRIPTS), "an address of an actant", "grammatical roles")
    assert_atmost_one_from(l, {INDEPENDANT_QUALITY}, "an address of an actant", "dependant")

    assert_only_one_from(l, ADDRESS_ACTANTS_DEFINITION_SCRIPTS, "an address of an actant", "definitions")

    assert_only_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_NUMBER_SCRIPTS, "an address of an actant", "grammatical numbers")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_CONTINUITY_SCRIPTS, "an address of an actant", "continuities")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_GRAMMATICAL_GENDER_SCRIPTS, "an address of an actant", "grammatical genders")

    assert_atmost_one_from(l, ADDRESS_ACTANTS_QUANTIFICATION_SCRIPTS, "an address of an actant", "quantifications")


def check_transformation_quality(l: List[Script]):
    assert_(len(l) == 0, "A quality can't have a transformation polymorpheme.")


CONTENT_TIME_POLYMORPHEME_SCRIPTS = {
    *script("t.o.-M:O:.-'").singular_sequences, # Qualité et relations temporelles
    *script("t.o.-n.o.-M:O:.-'").singular_sequences, # Unitées de temps du calendrier
    *script("t.i.-d.i.-t.+M:O:.-'").singular_sequences, # Unités de temps du chronomètre
}


ADDRESS_POLYMORPHEME_SCRIPTS = {
    *ADDRESS_PROCESS_POLYMORPHEME_SCRIPTS,

    *ADDRESS_ACTANT_SCRIPTS,

    *ADDRESS_TIME_POLYMORPHEME_SCRIPTS,


    *script("E:.-F:.M:M:.-l.-'").singular_sequences,  # distribution spacialle
    *script("").singular_sequences,  #

}



TRANSFORMATION_POLYMORPHEME_SCRIPTS = []