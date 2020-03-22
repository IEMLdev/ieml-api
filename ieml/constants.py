import _pygit2
import pygit2
from bidict import bidict
import os
from appdirs import user_cache_dir, user_data_dir

LIBRARY_VERSION = '1.0.3'

IEMLDB_DEFAULT_GIT_ADDRESS='https://github.com/IEMLdev/ieml-language.git'
# IEMLDB_DEFAULT_GIT_ADDRESS='https://github.com/ogrergo/ieml-language.git'

# DICTIONARY_FOLDER = os.path.abspath(os.path.join(__file__, '../../definition/dictionary'))
# LEXICONS_FOLDER = os.path.abspath(os.path.join(__file__, '../../definition/lexicons'))

VERSIONS_FOLDER = os.path.join(user_data_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'dictionary_versions')
CACHE_VERSIONS_FOLDER = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'cached_dictionary_versions')
PARSER_FOLDER = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), 'parsers')

os.makedirs(VERSIONS_FOLDER, exist_ok=True)
os.makedirs(PARSER_FOLDER, exist_ok=True)
os.makedirs(CACHE_VERSIONS_FOLDER, exist_ok=True)


def get_iemldb_folder(name):
    return os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION), name)



# DICTIONARY_SCHEMA_FILE = os.path.abspath(os.path.join(__file__, '../../definition/dictionary_paradigm_schema.yaml'))


GRAMMATICAL_CLASS_NAMES = bidict({
    0: 'AUXILIARY',
    1: 'VERB',
    2: 'NOUN',
})

AUXILIARY_CLASS = GRAMMATICAL_CLASS_NAMES.inv['AUXILIARY']
VERB_CLASS = GRAMMATICAL_CLASS_NAMES.inv['VERB']
NOUN_CLASS = GRAMMATICAL_CLASS_NAMES.inv['NOUN']

LANGUAGES = [
    'fr',
    'en'
]

CHARACTER_SIZE_LIMIT = 6
MAX_NODES_IN_SENTENCE = 20
MAX_DEPTH_IN_HYPERTEXT = 8
MAX_NODES_IN_HYPERTEXT = 20
MAX_SINGULAR_SEQUENCES = 360
MAX_SIZE_HEADER = 12
MAX_LAYER = 6

# max number of terms (arbitrary, this value was chosen for allocate the node id range for drupal)
MAX_TERMS_IN_DICTIONARY = 18999

LAYER_MARKS = [
    ':',
    '.',
    '-',
    '\'',
    ',',
    '_',
    ';'
]

PRIMITIVES = {
    'E',
    'U',
    'A',
    'S',
    'B',
    'T'
}

character_value = {
    'E': 0x1,
    'U': 0x2,
    'A': 0x4,
    'S': 0x8,
    'B': 0x10,
    'T': 0x20

}

remarkable_multiplication_lookup_table = {
    "U:U:": "wo", "U:A:": "wa", "U:S:": "y", "U:B:": "o", "U:T:": "e",
    "A:U:": "wu", "A:A:": "we", "A:S:": "u", "A:B:": "a", "A:T:": "i",
    "S:U:": "j",  "S:A:": "g",  "S:S:": "s", "S:B:": "b", "S:T:": "t",
    "B:U:": "h",  "B:A:": "c",  "B:S:": "k", "B:B:": "m", "B:T:": "n",
    "T:U:": "p",  "T:A:": "x",  "T:S:": "d", "T:B:": "f", "T:T:": "l"
}

REMARKABLE_ADDITION = {
    "O": {'U', 'A'},
    "M": {'S', 'B', 'T'},
    "F": {'U', 'A', 'S', 'B', 'T'},
    "I": {'E', 'U', 'A', 'S', 'B', 'T'}
}

PHONETIC_PUNCTUATION = [
    '',
    '.',
    '-',
    '..',
    '--',
    '_',
    '~'
]
TERM_REGEX = r'(?!E:\.b\.E:.:\.-)[EUASBTOMFIacbedgfihkjmlonpsutwyx][EUASBTOMFIacbedgfihkjmlonpsutwyx\.\-\;\:\,\'\’\_\+]+'

# TERM_REGEX_LAYER_0 = r'[EUASBTOMFI]\:'
# TERM_REGEX_LAYER_0_ADD = r'{layer0}(\s*\+\s*{layer0})*'.format(layer0=TERM_REGEX_LAYER_0)
#
# TERM_REGEX_LAYER_1 = r'([acbedgfihkjmlonpsutwyx]|{layer0}{rec})\.'.format(layer0=TERM_REGEX_LAYER_0_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_1_ADD = r'{layer1}(\s*\+\s*{layer1})*'.format(layer1=TERM_REGEX_LAYER_1)
#
# TERM_REGEX_LAYER_2 = r'{layer1}{rec}\-'.format(layer1=TERM_REGEX_LAYER_1_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_2_ADD = r'{layer2}(\s*\+\s*{layer2})*'.format(layer2=TERM_REGEX_LAYER_2)
#
# TERM_REGEX_LAYER_3 = r"{layer2}{rec}\'".format(layer2=TERM_REGEX_LAYER_2_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_3_ADD = r'{layer3}(\s*\+\s*{layer3})*'.format(layer3=TERM_REGEX_LAYER_3)
#
# TERM_REGEX_LAYER_4 = r"{layer3}{rec}\,".format(layer3=TERM_REGEX_LAYER_3_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_4_ADD = r'{layer4}(\s*\+\s*{layer4})*'.format(layer4=TERM_REGEX_LAYER_4)
#
# TERM_REGEX_LAYER_5 = r"{layer4}{rec}\_".format(layer4=TERM_REGEX_LAYER_4_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_5_ADD = r'{layer5}(\s*\+\s*{layer5})*'.format(layer5=TERM_REGEX_LAYER_5)
#
# TERM_REGEX_LAYER_6 = r"{layer5}{rec}\;".format(layer5=TERM_REGEX_LAYER_5_ADD, rec="{1,3}")
# TERM_REGEX_LAYER_6_ADD = r'{layer6}(\s*\+\s*{layer6})*'.format(layer6=TERM_REGEX_LAYER_6)
#
# TERM_REGEX = r'({layer0}|{layer1}|{layer2}|{layer3}|{layer4}|{layer5}|{layer6})'.format(layer0=TERM_REGEX_LAYER_0_ADD,
#                                                                                         layer1=TERM_REGEX_LAYER_1_ADD,
#                                                                                         layer2=TERM_REGEX_LAYER_2_ADD,
#                                                                                         layer3=TERM_REGEX_LAYER_3_ADD,
#                                                                                         layer4=TERM_REGEX_LAYER_4_ADD,
#                                                                                         layer5=TERM_REGEX_LAYER_5_ADD,
#                                                                                         layer6=TERM_REGEX_LAYER_6_ADD,)


STRUCTURE_KEYS = ['inhibition', 'is_root', 'is_ignored']

INHIBITABLE_RELATIONS=['father_substance',
                       'father_attribute',
                       'father_mode',
                       'opposed',
                       'associated',
                       'crossed',
                       'twin']

RELATIONS = [
            'contains',         # 0
            'contained',        # 1
            'father_substance', # 2
            'child_substance',  # 3
            'father_attribute', # 4
            'child_attribute',  # 5
            'father_mode',      # 6
            'child_mode',       # 7
            'opposed',          # 8
            'associated',       # 9
            'crossed',          # 10
            'twin',             # 11
            'table_0',
            'table_1',
            'table_2',
            'table_3',
            'table_4',
            'table_5',
            'identity',  # -1

             # 'inclusion',        # 12
             # 'father',           # 13
             # 'child',            # 14
             # 'etymology',        # 15
             # 'siblings',         # 16
             # 'table'             # 17
             ]

INVERSE_RELATIONS = {
    'father_substance': 'child_substance',
    'child_substance': 'father_substance',  # 3
    'father_attribute': 'child_attribute', # 4
    'child_attribute': 'father_attribute',  # 5
    'father_mode': 'child_mode',      # 6
    'child_mode': 'father_mode',
    'contains': 'contained',
    'contained': 'contains',
    'opposed':'opposed',          # 8
    'associated':'associated',       # 9
    'crossed': 'crossed',        # 10
    'twin': 'twin',
    'table_0': 'table_0',
    'table_1': 'table_1',
    'table_2': 'table_2',
    'table_3': 'table_3',
    'table_4': 'table_4',
    'table_5': 'table_5',
    'father': 'child',
    'child': 'father',
    'inclusion': 'inclusion',
    'etymology': 'etymology',        # 15
    'siblings': 'siblings',         # 16
    'table': 'table',
    'identity': 'identity'
}

MORPHEMES_GRAMMATICAL_MARKERS = {
    'E:.wo.-',
    'E:.wa.-', 'E:.wu.-', 'E:.we.-', 'E:'}

MORPHEME_SERIE_SIZE_LIMIT_CONTENT = 5
TRAIT_SIZE_LIMIT_CONTENT = 5
MORPHEME_SERIE_SIZE_LIMIT_FUNCTION = 3


POLYMORPHEME_MAX_MULTIPLICITY=3

DESCRIPTORS_CLASS = ['translations', 'comments', 'tags']

TYPES = ['morpheme', 'polymorpheme', 'lexeme', 'word', 'phrase']
DEFAULT_COMMITER_SIGNATURE = pygit2.Signature('ieml-commiter', 'commiter@ieml.io')