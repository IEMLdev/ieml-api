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

TYPES = ['morpheme', 'polymorpheme', 'word', 'phrase']
