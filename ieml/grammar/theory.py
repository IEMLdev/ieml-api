from itertools import chain

from .fact import Fact
from .usl import Usl
from ..constants import MAX_NODES_IN_SENTENCE
from ..exceptions import InvalidIEMLObjectArgument, InvalidTreeStructure
from .tree_graph import TreeGraph


def theory(clause_list, literals=None):
    try:
        _clauses = [(a, b, c) for a, b, c in clause_list]
    except TypeError:
        raise InvalidIEMLObjectArgument(Theory, "Invalid argument %s is not an iterable of triples" % str(clause_list))

    if _clauses == []:
        raise InvalidIEMLObjectArgument(Theory, "Invalid argument %s is empty" % str(clause_list))

    if any(not isinstance(e, Fact) for s in _clauses for e in s):
        raise InvalidIEMLObjectArgument(Theory, "Invalid argument %s is not a list of Fact triples" % str(clause_list))

    if any(a == b for a, b, c in _clauses):
        raise InvalidIEMLObjectArgument(Theory, "The attribute and the substance must be distinct for each triples")

    return Theory(_clauses, literals=literals)


class Theory(Usl):
    def __init__(self, clauses, literals=None):

        try:
            tree_graph = TreeGraph(clauses)
        except InvalidTreeStructure as e:
            raise InvalidIEMLObjectArgument(Theory, str(e))

        if len(tree_graph.nodes) > MAX_NODES_IN_SENTENCE:
            raise InvalidIEMLObjectArgument(Theory, "Too many distinct nodes: %d>%d." %
                                            (len(tree_graph.nodes), MAX_NODES_IN_SENTENCE))

        dictionary_version = clauses[0][0].dictionary_version
        if any(e.dictionary_version != dictionary_version for s in clauses for e in s):
            raise InvalidIEMLObjectArgument(Theory, "Incompatible dictionary version in the list of Fact triples")

        self.tree_graph = tree_graph
        self.children = tuple(e for stage in self.tree_graph.stages
                              for e in sorted((t[1] for s in stage for t in self.tree_graph.transitions[s])))

        super().__init__(self.tree_graph.root.dictionary_version, literals=literals)

    @property
    def grammatical_class(self):
        return self.tree_graph.root.grammatical_class

    def compute_str(self):
        return "[{0}]".format('+'.join(
            "({0}*{1}*{2})".format(str(a), str(b), str(c)) for a, b, c in self.children))

    def _do_gt(self, other):
        return self.children > other.children

    def __iter__(self):
        return self.facts.__iter__()

    def _get_words(self):
        return set(chain.from_iterable(c.words for c in self.facts))

    def _get_topics(self):
        return set(chain.from_iterable(c.topics for c in self.facts))

    def _get_facts(self):
        return set(chain.from_iterable(self.children))

    def _get_theories(self):
        return {self}

    def _set_version(self, version):
        for n in self.tree_graph.nodes:
            n.set_dictionary_version(version)
