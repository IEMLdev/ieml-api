from functools import reduce
from itertools import product, combinations, chain
from operator import mul
from typing import List, Union

from ieml.lexicon.grammar.character import Character, character

from ieml.dictionary.script import Script, script
from ieml.lexicon.grammar.usl import Literal
from .usl import Usl
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.constants import MAX_SINGULAR_SEQUENCES, CHARACTER_SIZE_LIMIT


def _character(semes: List[Union[Script, str]]):
    if not semes:
        return [script('E:')]

    try:
        _semes = [script(e) for e in semes]
    except TypeError:
        raise InvalidIEMLObjectArgument(Character, "The root argument %s is not an iterable" % str(semes))

    if len(_semes) > CHARACTER_SIZE_LIMIT:
        raise InvalidIEMLObjectArgument(Character, "Invalid semes count %d, must be lower or equal than %d."
                                        % (len(_semes), CHARACTER_SIZE_LIMIT))

    if any(not isinstance(c, Script) for c in _semes):
        raise InvalidIEMLObjectArgument(Character, "The children of a Topic must be a Word instance.")

    singular_sequences = [s for t in _semes for s in t.singular_sequences if not s.empty]
    if len(singular_sequences) != len(set(s for s in singular_sequences if not s.empty)):
        raise InvalidIEMLObjectArgument(Character, "Singular sequences intersection in %s." %
                                        str([str(t) for t in _semes]))

    return _semes


def word(substance: List[Union[str, Script]] = None,
         attribute: List[Union[str, Script]] = None,
         mode: List[Union[str, Script]] = None,
         literals:Literal = None):

    substance = _character(substance)
    attribute = _character(attribute)
    mode = _character(mode)

    return Word(substance, attribute, mode, literals=literals)


class Word(Usl):
    def __init__(self,
                 substance: List[Script],
                 attribute: List[Script],
                 mode: List[Script],
                 literals:Literal = None):

        self.substance = substance
        self.attribute = attribute
        self.mode = mode
        self.characters = [self.substance, self.attribute, self.mode]

        super().__init__(literals=literals)

        if self.cardinal > MAX_SINGULAR_SEQUENCES:
            raise InvalidIEMLObjectArgument(Word, "Too many Topic- singular sequences defined (max: 360): %d" % self.cardinal)

        self.singular_sequences = self._build_singular_sequences()
        self.ancestors = self._build_ancestors()

    def _build_singular_sequences(self):
        characters = []
        for char in self.characters:
            characters.append(list(product(*[s.singular_sequences for s in char])))

        singular_sequences = [w for w in product(*characters)]
        if len(singular_sequences) == 1:
            return {self}

        return {word(*w) for w in singular_sequences}

    def _build_ancestors(self):
        characters = []
        for char in self.characters:
            characters.append(list(chain.from_iterable(combinations(char, i) for i in range(1, len(char) + 1))))

        ancestors = {w for w in product(*characters)}
        #remove self
        return {word(*w) for w in ancestors if not all(len(w[i]) == len(char) for i, char in enumerate(self.characters))}

    def __len__(self):
        return self.cardinal

    def __contains__(self, item):
        if isinstance(item, Word):
            return item.singular_sequences.issubset(self.singular_sequences)

        return super().__contains__(item)

    def __iter__(self):
        return self.characters.__iter__()

    @property
    def grammatical_class(self):
        return max(s.script_class for s in self.substance)

    @property
    def layer(self):
        return sum(not s.empty for s in self.semes)

    def _get_cardinal(self):
        return reduce(mul, [w.cardinal for char in [self.substance, self.attribute, self.mode] for w in char], 1)

    @staticmethod
    def _char_str(char):
        return "({0})".format("+".join("[{}]".format(str(e)) for e in char))

    def compute_str(self):
        return "[{0}*{1}*{2}]".format(self._char_str(self.substance),
                                      self._char_str(self.attribute),
                                      self._char_str(self.mode))

    def _do_gt(self, other):
        return (self.substance, self.attribute, self.mode) > (other.substance, other.attribute, other.mode)

    def _get_semes(self):
        return set(self.attribute + self.substance + self.mode)

    def _get_words(self):
        return {self}

    def _get_facts(self):
        return set()

    def _get_theories(self):
        return set()