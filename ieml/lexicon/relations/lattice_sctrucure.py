from collections import defaultdict
from itertools import product
from typing import List

from ieml.lexicon.grammar import Word


class LatticeNode:
    def __init__(self, word, contains, contained_by, parents, child):
        self.word = word
        self.parents = sorted(parents)
        self.child = sorted(child)
        self.contains = sorted(contains)
        self.contained_by = sorted(contained_by)


class LatticeStructure:
    def __init__(self, words):
        self.words_to_latticeNode, self.roots = self._build_hierarchie(words)

    def __getitem__(self, item) -> LatticeNode :
        return self.words_to_latticeNode[item]

    @staticmethod
    def _build_hierarchie(words: List[Word]):
        word_to_parents = {w: set() for w in words}
        word_to_child = {w: set() for w in words}
        word_to_contains = {w: set() for w in words}
        word_to_contained_by = {w: set() for w in words}

        for w0 in words:
            for w1 in w0.ancestors:
                if w1 in word_to_parents:
                    word_to_parents[w0].add(w1)
                    word_to_child[w1].add(w0)

            for w1 in w0.singular_sequences:
                if w1 in word_to_parents:
                    word_to_contains[w0].add(w1)
                    word_to_contained_by[w1].add(w0)

        words_to_lattice = {w: LatticeNode(w,
                                           parents=parents,
                                           child=word_to_child[w],
                                           contains=word_to_contains[w],
                                           contained_by=word_to_contained_by[w]) for w, parents in word_to_parents.items()}

        roots = [words_to_lattice[w] for w, parents in word_to_parents.items() if not parents]

        return words_to_lattice, roots