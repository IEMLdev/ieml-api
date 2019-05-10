from itertools import chain, combinations, count, product
from typing import List

from collections import defaultdict, OrderedDict

from ieml.constants import MORPHEME_SERIE_SIZE_LIMIT_CONTENT, \
    TRAIT_SIZE_LIMIT_CONTENT, MORPHEMES_GRAMMATICAL_MARKERS
from ieml.dictionary.script import Script


class LastUpdatedOrderedDict(OrderedDict):
    'Store items in the order the keys were last added'
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)


class LexicalItem:
    def __init__(self):
        self._singular_sequences = None
        self._str = None

    def __str__(self):
        return self._str

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        """Since the IEML string for a script is its definition, it can be used as a hash"""
        return self._str.__hash__()

    @property
    def singular_sequences(self):
        if self._singular_sequences is None:
            self._singular_sequences = self._compute_singular_sequences()

        return self._singular_sequences

    def _compute_singular_sequences(self):
        raise NotImplementedError

    def __len__(self):
        return self.cardinal

    @property
    def cardinal(self):
        return len(self.singular_sequences)


    def __contains__(self, item):
        assert isinstance(item, self.__class__)
        if item.cardinal == 1:
            return item in self.singular_sequences
        else:
            return set(item.singular_sequences).issubset(set(self.singular_sequences))


def check_morpheme_serie(ms):
    assert all(isinstance(s, Script) for s in ms.constant), "A morpheme serie constant must be made of morphemes"
    assert all(isinstance(g[0], tuple) and all(isinstance(gg, Script) for gg in g[0])
               and isinstance(g[1], int) for g in ms.groups), \
        "A morpheme serie group must be made of a list of (Morpheme list, multiplicity)"

    assert tuple(sorted(ms.groups)) == ms.groups
    assert tuple(sorted(ms.constant)) == ms.constant

    all_group = [ms.constant, *(g for g, _ in ms.groups)]
    all_morphemes = {str(w): w for g in all_group for w in g}

    assert len(all_morphemes) == sum(len(g) for g in all_group), "The groups and constants must be disjoint"


class MorphemeSerie(LexicalItem):
    def __init__(self, constant: List[Script]=(), groups=()):
        super().__init__()

        self.constant = tuple(sorted(constant))
        self.groups = tuple((tuple(g[0]), g[1]) for g in sorted(groups))

        self._str = ' '.join(chain(map(str, self.constant),
                               ["m{}({})".format(mult, ' '.join(map(str, group))) for group, mult
                                    in self.groups]))

    @property
    def empty(self):
        return not self.constant and not self.groups

    def __lt__(self, other):
        return self.constant < other.constant or \
               (self.constant == other.constant and self.groups < other.groups)


    def _compute_singular_sequences(self):
        if not self.groups:
            return [self]

        # G0, G1, G2 Groups
        # Gi = {Gi_a, Gi_b, ... Words}

        # combinaisons 1: C1
        # 001 -> G0_a, G0_b, ...
        # 010 -> G1_a, ...
        # 100
        # combinaisons 2: C2
        # 011 -> G0_a + G1_a, G0_a + G1_b, ..., G0_b + G1_a, ...
        # 110 -> G1_a + G2_a, G1_a + G2_b, ..., G1_b + G2_a, ...
        # 101
        # combinaisons 3: C3
        # 111 -> G0_a + G1_a + G2_a, ...

        # combinaisons 4: C4
        # 112
        # 121
        # 211

        # combinaisons i: Ci
        # // i = q * 3 + r
        # // s = q + 1
        # r == 0:
        # qqq
        # r == 1:
        # qqs
        # qsq
        # sqq
        # r == 2:
        # qss
        # sqs
        # ssq

        # abcde... = iter (a Words parmi G0) x (b words parmi G1) x (c words parmi G2) x ...
        # Ci = iter {abb, bab, bba}
        #   i = q * 3 + r
        #   a = q + (1 si r = 1 sinon 0)
        #   b = q + (1 si r = 2 sinon 0)

        # Min = min len Groups
        # Max = max len Groups

        # C3 + C2
        # etc...

        # number of groups
        N = len(self.groups)
        min_len = min(map(len, list(zip(*self.groups))[0]))

        max_sizes_groups = defaultdict(set)
        for i, (grp, mult) in enumerate(self.groups):
            for j in range(mult + 1, min_len + 1):
                max_sizes_groups[j].add(i)

        def iter_groups_combinations():
            for i in count():
                # minimum number of elements taken from each groups
                q = i // N

                # number of groups which will yield q + 1 elements
                r = i % N

                if q == min_len + 1 or q in max_sizes_groups:
                    break

                for indexes in combinations(range(N), r):
                    if any(j in max_sizes_groups.get(q + 1, set()) for j in indexes):
                        continue

                    if any(len(self.groups[i][0]) <= q for i in indexes):
                        continue

                    yield from product(*(combinations(self.groups[i][0], q + 1) for i in indexes),
                                       *(combinations(self.groups[i][0], q) for i in range(N) if i not in indexes))

        morphemes_series = LastUpdatedOrderedDict()

        SIZE_LIMIT = MORPHEME_SERIE_SIZE_LIMIT_CONTENT# if is_content else MORPHEME_SERIE_SIZE_LIMIT_FUNCTION

        for gs in iter_groups_combinations():
            morpheme_semes = list(set(chain(*gs, self.constant)))
            if len(morpheme_semes) == 0 or len(morpheme_semes) > SIZE_LIMIT:
                continue

            m = MorphemeSerie(constant=morpheme_semes)
            morphemes_series[str(m)] = m

        return tuple(morphemes_series.values())


def check_trait(trait):
    check_morpheme_serie(trait.core)
    check_morpheme_serie(trait.periphery)

    # assert tuple(sorted(trait.core)) == trait.core
    # assert tuple(sorted(trait.periphery)) == trait.periphery

    # assert all(isinstance(s, Script) and s in dictionary.scripts for s in trait.content + trait.periphery), \
    #     "Script not defined in dictionary"
    # assert all(isinstance(g, tuple) and isinstance(g[0], int) and
    #            all(isinstance(s, Script) and s in dictionary.scripts for s in g[1])
    #            for g in trait.groups_content + trait.groups_periphery), "Invalid groups"

    # assert all(not s.paradigm for s in [*trait.core, *trait.periphery, *list(zip(*trait.groups_content))[1],
    #            *list(zip(*trait.groups_periphery))[1]]), "A trait must contains only morphemes singulars sequences"


class Trait(LexicalItem):
    """ <<morph morph> morph morph>"""
    def __init__(self, core: MorphemeSerie, periphery: MorphemeSerie):
        super().__init__()

        self.core = core
        self.periphery = periphery

        self._str = '<{}>'.format('<{}> {}'.format(str(self.core), str(self.periphery)).strip())

    def __lt__(self, other):
        if isinstance(other, Trait):
            return self.core < other.core or \
                   (self.core != other.core and self.periphery < other.periphery)
        else:
            return super().__lt__(other)

    def _compute_singular_sequences(self):
        if self.core.cardinal == 1 and self.periphery.cardinal == 1:
            return [self]

        traits = LastUpdatedOrderedDict()

        for core, periph in product(self.core.singular_sequences, self.periphery.singular_sequences):
            morphemes = list(chain(core.constant, periph.constant))
            if len(morphemes) == 0 or len(morphemes) > TRAIT_SIZE_LIMIT_CONTENT:
                continue

            t = Trait(core=core, periphery=periph)
            traits[str(t)] = t

        return tuple(traits.values())

    @property
    def empty(self):
        return self.core.empty and self.periphery.empty

def check_character(c):
    assert (c.empty and len(c.functions) == 0 and c.content.empty and c.klass.empty) or not c.empty, \
        "Empty character must have the E: grammatical class, an empty content and no functions."
    assert not c.content.empty or (len(c.functions) != 0 and c.content.empty), \
        "An empty content cannot have a function"
    assert all(isinstance(t, Trait) for t in [c.content, *c.functions]), "A character must be made of Trait"
    assert isinstance(c.klass, Script), "A character must indicate its class with a morpheme from [{}]"\
        .format(', '.join(MORPHEMES_GRAMMATICAL_MARKERS))
    assert all(f.periphery.empty for f in c.functions), "The perifery must be empty the function traits of a character"

    check_trait(c.content)
    for f in c.functions:
        check_trait(f)

class Character(LexicalItem):
    """[<morpheme_klass> trait_content trait_function0 trait_function1]"""

    def __init__(self, klass: Script, content: Trait, functions: List[Trait]=()):
        super().__init__()

        self.klass = klass
        self.content = content
        self.functions = tuple(sorted(functions))


        if self.empty:
            self._str = "[<{}>]".format(str(self.klass))
        else:
            self._str = "[{}]".format(
                "<{}> {}".format(str(self.klass),
                                 " ".join([str(self.content)] + [str(f) for f in self.functions])).strip())

    @property
    def empty(self):
        return self.klass.empty

    def _compute_singular_sequences(self):
        if all(t.cardinal == 1 for t in [self.content] + list(self.functions)):
            return [self]

        traits = [self.content] + list(self.functions)

        characters = LastUpdatedOrderedDict()

        for tt in product(*[t.singular_sequences for t in traits]):
            # morphemes = list(chain(core.constant, periph.constant))
            # if len(morphemes) == 0 or len(morphemes) > TRAIT_SIZE_LIMIT_CONTENT:
            #     continue

            t = Character(klass=self.klass, content=tt[0], functions=tt[1:])
            characters[str(t)] = t

        return tuple(characters.values())

def check_words(w):
    check_character(w.substance)
    check_character(w.attribute)
    check_character(w.mode)


class Word(LexicalItem):
    """(character*character*character)"""
    def __init__(self, substance: Character, attribute: Character, mode: Character):
        super().__init__()

        self.substance = substance
        self.attribute = attribute
        self.mode = mode
        self._str = '({})'.format("*".join([str(self.substance), str(self.attribute), str(self.mode)]))

    @property
    def empty(self):
        return self.substance.empty and self.attribute.empty and self.mode.empty

    def _compute_singular_sequences(self):
        if all(t.cardinal == 1 for t in [self.substance, self.attribute, self.mode]):
            return [self]

        words = LastUpdatedOrderedDict()

        for s, a, m in product(self.substance.singular_sequences,
                          self.attribute.singular_sequences,
                          self.mode.singular_sequences):

            w = Word(substance=s, attribute=a, mode=m)
            words[str(w)] = w

        return tuple(words.values())
