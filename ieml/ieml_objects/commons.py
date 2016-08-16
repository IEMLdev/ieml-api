from collections import defaultdict

import numpy

from ieml.commons import TreeStructure
from ieml.exceptions import NoRootNodeFound, SeveralRootNodeFound, NodeHasNoParent, NodeHasTooMuchParents


class IEMLObjects(TreeStructure):
    def __init__(self):
        super().__init__()


class TreeGraph():
    def __init__(self, list_transitions):
        """
        Transitions list must be the (start, end, data) the data will be stored as the transition tag
        :param list_transitions:
        """
        # transitions : dict
        #
        self.transitions = defaultdict(lambda :list())
        for t in list_transitions:
            self.transitions[t[0]].append((t[1], t[2]))

        self.nodes = list({self.transitions} | {e[0] for l in self.transitions.values() for e in l})
        self.nodes_index = {n: i for i, n in enumerate(self.nodes)}
        _count = len(self.nodes)
        self.array = numpy.zeros((len(self.nodes), len(self.nodes)), dtype=bool)

        for t in self.transitions:
            for end in t:
                self.array[self.nodes_index[t]][self.nodes_index[end[0]]] = True

        # checking
        # root checking, no_parent hold True for each index where the node has no parent
        parents_count = numpy.dot(self.array.transpose().astype(dtype=int), numpy.ones((_count,), dtype=int))
        no_parents = parents_count == 0
        roots_count = numpy.count_nonzero(no_parents)

        if roots_count == 0:
            raise NoRootNodeFound()
        elif roots_count > 1:
            raise SeveralRootNodeFound()

        self.root = self.nodes[no_parents.nonzero()[0][0]]

        if (parents_count > 1).any():
            raise NodeHasTooMuchParents()

        def __stage():
            current = [self.root]
            while current != []:
                yield current
                current = [child[0] for parent in current for child in self.transitions[parent]]

        self.stages = list(__stage())