from bidict import bidict


GRAMMATICAL_CLASS_NAMES = bidict({
    0: 'AUXILIARY',
    1: 'VERB',
    2: 'NOUN'
})

AUXILIARY_CLASS = GRAMMATICAL_CLASS_NAMES.inv['AUXILIARY']
VERB_CLASS = GRAMMATICAL_CLASS_NAMES.inv['VERB']
NOUN_CLASS = GRAMMATICAL_CLASS_NAMES.inv['NOUN']

LANGUAGES = {
    'fr',
    'en'
}

MORPHEME_SIZE_LIMIT = 6
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