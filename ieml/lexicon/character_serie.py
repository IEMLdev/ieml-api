from itertools import product, combinations, chain, count
from typing import List, Sequence, Union, Tuple

from collections import defaultdict, OrderedDict

from ieml.constants import CHARACTER_SIZE_LIMIT
from ieml.dictionary.dictionary import Translations
from ieml.dictionary.script import Script
from ieml.lexicon.grammar import word, Word


class LastUpdatedOrderedDict(OrderedDict):
    'Store items in the order the keys were last added'
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)


class SemesGroup:
    def __init__(self, semes: List[Script], multiplicity: Union[int, None]):
        self.semes = tuple(semes)
        self.multiplicity = multiplicity

    def __len__(self):
        return len(self.semes)

    def __iter__(self):
        return iter(self.semes)

    def __next__(self):
        return next(self.semes)

    def __getitem__(self, item):
        return self.semes[item]


class CharacterSerie:
    def __init__(self, translations: Translations,
                 groups: Sequence[SemesGroup],
                 constant: SemesGroup):

        self.translations = translations
        self.groups = list(groups)
        self.constant = constant

        self.morphemes = self._build_morphemes(self.groups, self.constant)

    @staticmethod
    def _build_morphemes(groups: List[SemesGroup], constant: SemesGroup) -> Tuple[Word]:
        # constants = seconstants
        # groups = [words_of_repertory(r) for r in groups]

        all_group = list(groups) + [constant]
        all_semes = {str(w): w for g in all_group for w in g}

        if len(all_semes) != sum(len(c) for c in all_group):
            raise ValueError("The groups and constants must be disjoint")

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
        N = len(groups)
        min_len = min(map(len, groups))

        max_sizes_groups = defaultdict(set)
        for i, grp in enumerate(groups):
            for j in range(grp.multiplicity + 1, min_len + 1):
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

                    if any(len(groups[i]) <= q for i in indexes):
                        continue

                    yield from product(*(combinations(groups[i], q + 1) for i in indexes),
                                       *(combinations(groups[i], q) for i in range(N) if i not in indexes))

        morphemes = LastUpdatedOrderedDict()

        for gs in iter_groups_combinations():
            morpheme_semes = list(chain(*gs, constant))
            if len(morpheme_semes) == 0 or len(morpheme_semes) > CHARACTER_SIZE_LIMIT:
                continue

            m = word(morpheme_semes)
            morphemes[str(m)] = m

        return tuple(morphemes.values())

