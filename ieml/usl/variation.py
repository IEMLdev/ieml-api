from itertools import combinations

from ieml.constants import POLYMORPHEME_MAX_MULTIPLICITY
from ieml.dictionary.script import Script, NullScript
from ieml.dictionary.script.script import NULL_SCRIPTS
from ieml.usl import USL


class Variation(USL):
    pass



class PolyMorphemeVariation(Variation):
    def __init__(self, items, multiplicity):
        super().__init__()
        self.items = tuple(sorted(items))
        self.multiplicity = multiplicity
        self._singular_sequences = self._compute_singular_sequences()

    def _compute_singular_sequences(self):
        res = [(NULL_SCRIPTS[0],)]

        if len(self.items) == 0:
            return res

        for i in range(0, self.multiplicity):
            for m in combinations(self.items, i + 1):
               res.append(tuple(m))

        from ieml.usl import PolyMorpheme

        return tuple(PolyMorpheme(constant=list(r)) for r in res)

    @property
    def empty(self):
        return len(self.items) != 0

    def check(self):
        return all(isinstance(e, Script) and e.cardinal == 1 for e in self.items) and isinstance(self.multiplicity, int) \
               and self.multiplicity < POLYMORPHEME_MAX_MULTIPLICITY

    def do_lt(self, other):
        return (self.items, self.multiplicity) < (other.items, other.multiplicity)

    def iter_structure(self, auto_promote_to_USL=False):
        yield from self.items

    def iter_structure_path(self, flexion=False):
        for i in self.items:
            yield

    @property
    def morphemes(self):
        return self.items
