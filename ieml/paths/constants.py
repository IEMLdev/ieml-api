from bidict._bidict import bidict

COORDINATES_KINDS = ('t', 's', 'a', 'm', 'r', 'f')

RANKS = bidict({
    0: 'Term',
    1: 'Word',
    2: 'Sentence',
    3: 'SuperSentence',
    4: 'Text'
})

KIND_TO_RANK = {
    't': RANKS.inv['Text'],
    'r': RANKS.inv['Word'],
    'f': RANKS.inv['Word']
}