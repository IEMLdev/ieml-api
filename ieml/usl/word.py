from itertools import chain, product
from typing import List

from ieml.commons import LastUpdatedOrderedDict
from ieml.constants import MORPHEMES_GRAMMATICAL_MARKERS
from ieml.dictionary.script import Script
from ieml.usl import USL
from ieml.usl.polymorpheme import PolyMorpheme, check_polymorpheme


def check_word(c):
    assert (c.empty and len(c.functions) == 0 and c.content.empty and c.klass.empty) or not c.empty, \
        "Empty character must have the E: grammatical class, an empty content and no functions."
    assert (c.contents and not all(pm.empty for pm in c.contents)) or (len(c.functions) != 0 and c.content.empty), \
        "An empty content cannot have a function"
    assert all(isinstance(t, PolyMorpheme) for t in c.poly_morphemes), "A character must be made of Trait"
    assert isinstance(c.klass, Script), "A character must indicate its class with a morpheme from [{}]"\
        .format(', '.join(MORPHEMES_GRAMMATICAL_MARKERS))

    for cc in c.contents:
        check_polymorpheme(cc)
    for f in c.functions:
        for pm in f:
            check_polymorpheme(pm)


class Word(USL):
    """[<morpheme_klass> trait_content trait_function0 trait_function1]"""

    def __init__(self, klass: Script, contents: List[PolyMorpheme]=(), functions: List[List[PolyMorpheme]]=()):
        super().__init__()

        self.klass = klass
        self.contents = tuple(sorted(contents))
        self.functions = tuple(tuple(sorted(f)) for f in functions)

        if self.empty:
            self._str = "[{}]".format(str(self.klass))
        else:
            res = ' > '.join(' '.join("({})".format(str(pm)) for pm in c) for c in chain([self.contents], self.functions))

            self._str = "[{} > {}]".format(str(self.klass), res)

        self.grammatical_class = self.klass

    @property
    def empty(self):
        return self.klass.empty

    @property
    def poly_morphemes(self):
        return [*self.contents, *chain(*self.functions)]

    def _compute_singular_sequences(self):
        if all(pm.cardinal == 1 for pm in self.poly_morphemes):
            return [self]

        all_poly = [(pm, i) for i, layer in enumerate([self.contents] + list(self.functions)) for pm in layer]
        all_poly, layers = list(zip(*all_poly))

        words = LastUpdatedOrderedDict()

        for tt in product(*[pm.singular_sequences for pm in all_poly]):
            res = [[] for _ in range(max(layers) + 1)]
            for ss, i in zip(tt, layers):
                res[i].append(ss)

            t = Word(klass=self.klass, contents=res[0], functions=res[1:])

            words[str(t)] = t

        return tuple(words.values())
