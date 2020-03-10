from itertools import product, combinations, chain, count

from collections import defaultdict
from typing import List

from ieml.commons import LastUpdatedOrderedDict
from ieml.constants import MORPHEME_SERIE_SIZE_LIMIT_CONTENT, AUXILIARY_CLASS, POLYMORPHEME_MAX_MULTIPLICITY
from ieml.dictionary.script import Script
from ieml.dictionary.script.script import NULL_SCRIPTS
from ieml.usl import USL


def check_polymorpheme(ms):
    if not all(isinstance(s, Script) for s in ms.constant):
        raise ValueError("A polymorpheme constant must be made of morphemes")

    if not all(isinstance(g[0], tuple) and all(isinstance(gg, Script) for gg in g[0])
               and isinstance(g[1], int) for g in ms.groups):
        raise ValueError("A trait group must be made of a list of (Morpheme list, multiplicity)")

    if sorted(ms.groups) != list(ms.groups):
        raise ValueError("Invalid ordering of the polymorpheme groups")

    if any(sorted(g[0]) != list(g[0]) for g in ms.groups):
        raise ValueError("Invalid ordering of the morphemes in a polymorpheme groups")

    if any(g[0] and (int(g[1]) != g[1] or g[1] <= 0 or g[1] > POLYMORPHEME_MAX_MULTIPLICITY) for g in ms.groups):
        raise ValueError("Multiplicity is not a positive integer in [1, 2, 3].")

    if any(g[0] and g[1] > len(g[0])  for g in ms.groups):
        raise ValueError("Multiplicity is greater than the number of morphemes in the group.")

    if sorted(ms.constant) != list(ms.constant):
        raise ValueError("Invalid ordering of the polymorpheme constants")

    # compare the intersection except empty "E:"
    all_group = [ms.constant, *(_filter_empty(g) for g, _ in ms.groups)]
    all_morphemes = {str(w): w for g in all_group for w in g}

    if len(all_morphemes) != sum(len(g) for g in all_group):
        raise ValueError("The groups and constants must be disjoint")

    if any(len(m) != 1 for m in all_morphemes.values()):
        raise ValueError("A polymorpheme can't be made from a morpheme paradigm.")


def _filter_empty(l):
    return list(filter(lambda m: not m.empty, l))


class PolyMorpheme(USL):
    syntactic_level = 1

    def __init__(self, constant: List[Script]=(), groups=()):
        super().__init__()

        self.constant = tuple(sorted(_filter_empty(constant)))

        self.groups = tuple(sorted((tuple(sorted(g[0])), g[1]) for g in groups))

        self._str = ' '.join(chain(map(str, self.constant),
                               ["m{}({})".format(mult, ' '.join(map(str, group))) for group, mult
                                    in self.groups]))

        if not self.constant:
            self.constant = (NULL_SCRIPTS[0],)

        self.grammatical_class = max((s.grammatical_class for s in self.constant),
                                     default=AUXILIARY_CLASS)
    @property
    def empty(self):
        return not self.groups and len(self.constant) == 1 and self.constant[0].empty

    def check(self):
        check_polymorpheme(self)

    def do_lt(self, other):
        return len(self.constant) < len(other.constant) or \
               (len(self.constant) == len(other.constant) and self.constant < other.constant) or \
               (self.constant == other.constant and self.groups < other.groups)

    def iter_structure(self):
        yield from self.morphemes

    def iter_structure_path(self):
        from ieml.usl.decoration.path import PolymorphemePath, GroupIndex

        yield from [(PolymorphemePath(GroupIndex.CONSTANT, m), m) for m in self.constant]
        if len(self.groups) > 0:
            yield from [(PolymorphemePath(GroupIndex.GROUP_0, s), s) for s in self.groups[0][0]]

        if len(self.groups) > 1:
            yield from [(PolymorphemePath(GroupIndex.GROUP_1, s), s) for s in self.groups[1][0]]

        if len(self.groups) > 2:
            yield from [(PolymorphemePath(GroupIndex.GROUP_2, s), s) for s in self.groups[2][0]]

    @property
    def morphemes(self):
        return sorted(set(list(self.constant) + [m for g in self.groups for m in g[0]]))

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

        traits = LastUpdatedOrderedDict()

        SIZE_LIMIT = MORPHEME_SERIE_SIZE_LIMIT_CONTENT# if is_content else MORPHEME_SERIE_SIZE_LIMIT_FUNCTION

        for gs in iter_groups_combinations():
            morpheme_semes = list(set(chain(*gs, self.constant)))
            if len(morpheme_semes) == 0 or len(morpheme_semes) > SIZE_LIMIT:
                continue

            m = PolyMorpheme(constant=morpheme_semes)
            traits[str(m)] = m

        return tuple(traits.values())
