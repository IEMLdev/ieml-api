from ieml.dictionary.script import Script
from .usl import USL
from .polymorpheme import PolyMorpheme, check_polymorpheme
from .lexeme import Lexeme, check_lexeme
from .word import Word, check_word
# from .phrase import Phrase, check_phrase

from string import ascii_uppercase, ascii_lowercase, digits

alphanumeric = sorted(digits + ascii_uppercase + ascii_lowercase)

def int2base(i, max=30, characters=alphanumeric):
    assert i >= 0

    q = i // len(characters)
    r = i - q * len(characters)

    if q != 0:
        return int2base(q, max - 1, characters) + characters[r]
    else:
        return '0'*(max - 1) + characters[r]


def _polymorph_idx(pm, dic):
    return sum(len(dic.scripts) ** i * dic.index[ss] for i, ss in enumerate(pm.constant))



def get_index(s, dic):
    if isinstance(s, Script):
        return (0, '0' + int2base(dic.index[s]))

    if isinstance(s, PolyMorpheme):
        if len(s.constant) == 1 and len(s.groups) == 0:
            return (0, '0' + int2base(dic.index[s.constant[0]]))
        else:
            return (1, '1' + int2base(_polymorph_idx(s, dic)))
    elif isinstance(s, Word):
        return (2, '2' + int2base(0))
    else:
        return (3, '3' + int2base(0))
