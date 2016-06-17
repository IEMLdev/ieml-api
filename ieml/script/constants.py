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

PRIMITVES = {
    'E',
    'U',
    'A',
    'S',
    'B',
    'T'
}

character_value = {
    'E': 0b000001,
    'U': 0b000010,
    'A': 0b000100,
    'S': 0b001000,
    'B': 0b010000,
    'T': 0b100000

}
LAYER_MARKS = [
    ':',
    '.',
    '-',
    '\'',
    ',',
    '_',
    ';'
]

# Name of the relation (in db)
# if modification, need a db script reload
# remarkable siblings
OPPOSED_SIBLING_RELATION = 'OPPOSED_SIBLING'
ASSOCIATED_SIBLING_RELATION = 'ASSOCIATED_SIBLING'
CROSSED_SIBLING_RELATION = 'CROSSED_SIBLING'
TWIN_SIBLING_RELATION = 'TWIN_SIBLING'

# contains/contained
CONTAINED_RELATION = 'CONTAINED'
CONTAINS_RELATION = 'CONTAINS'

# Father/child
FATHER_RELATION = 'FATHER_RELATION'
CHILD_RELATION = 'CHILD_RELATION'

ELEMENTS = 'ELEMENTS'
SUBSTANCE = 'SUBSTANCE'
ATTRIBUTE = 'ATTRIBUTE'
MODE = 'MODE'

MAX_LAYER = 6

INHIBIT_RELATIONS = [
    OPPOSED_SIBLING_RELATION,
    ASSOCIATED_SIBLING_RELATION,
    CROSSED_SIBLING_RELATION,
    TWIN_SIBLING_RELATION,
    FATHER_RELATION + '.' + SUBSTANCE,
    FATHER_RELATION + '.' + ATTRIBUTE,
    FATHER_RELATION + '.' + MODE,
    CHILD_RELATION + '.' + SUBSTANCE,
    CHILD_RELATION + '.' + ATTRIBUTE,
    CHILD_RELATION + '.' + MODE,

]