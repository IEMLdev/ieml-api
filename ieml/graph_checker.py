import numpy as np

from ieml.exceptions import IndistintiveTermsExist, EmptyWordSubstance, NoRootNodeFound, SeveralRootNodeFound, \
    NodeHasNoParent, NodeHasTooMuchParents


class BasicGraphChecker:
    """Takes care of checking if a graph describing an IEMl proposition respects the IEML structura
    rules """

    def __init__(self, graph):
        self.adjacency_matrix = graph.adjacency_matrix
        self.node_count = self.adjacency_matrix.shape[0]
        self.ones_bool = np.full(self.node_count, True, dtype=bool)
        self.ones_int = np.full(self.node_count, 1,  dtype=int)
        self.row_xor = np.dot(self.adjacency_matrix, self.ones_bool)
        self.column_xor = np.dot(self.adjacency_matrix.transpose(), self.ones_bool)

    def _check_has_unique_root(self):
        """Using the adjacency matrix, checks that the graph has a unique root, and that this root
        has at least one child"""
        # checking the "root count"
        root_count = np.dot(self.column_xor.astype(dtype=int), self.column_xor.astype(dtype=int))
        if root_count == 0: # only one root
            raise NoRootNodeFound()
        elif root_count > 1:# more than one root
            raise SeveralRootNodeFound()
        else :
            #saving the index of the root_node
            for index, node_xor in enumerate(self.column_xor):
                if not node_xor:
                    self.root_node_index = index

    def _check_only_one_parent(self):
        """checks that each element of the graph only has one parent (making the graph a tree).
        This check depends on the root_node check """
        # getting the "incoming" vertices count for each node in an array
        incoming_connection_count = np.dot(self.adjacency_matrix.astype(dtype=int), self.ones_int)

        # for all node, except the root, there can and should only be ONE parent.
        for index, conn_sum in enumerate(incoming_connection_count):
            if conn_sum != 1 and index != self.root_node_index:
                if conn_sum > 1:
                    raise NodeHasTooMuchParents(index)
                else:
                    raise NodeHasNoParent(index)


class PhraseGraphChecker(BasicGraphChecker):
    """Adds a couple of verifications that are special to phrases"""
    pass


class SuperPhraseChecker(BasicGraphChecker):
    """Adds a couple of verifications that are special to super-phrase"""
    pass


class WordGraphChecker:
    """Checks the validity of a word's graph. Has nothing do to with the other regular graph checker"""

    def __init__(self, graph):
        self.subst_nodes = graph.subst_list
        self.attr_nodes = graph.attr_list

    def _check_morpheme(self, nodes_list):
        """checks the elements of a morpheme, namely, :
        - all distinct
        - not intersecting
        - well ordered"""
        # TODO : ordering and intersection

        #basically just checking for distinct terms
        if len(nodes_list) != len(set([node.id for node in nodes_list])):
            raise IndistintiveTermsExist()

    def check(self, word_graph):
        """Checks that the WordGraph conforms to the rules defined for both words and morphemes"""
        # for now, basically just checks that the Substance isn't empty and that all terms are distinct

        if not word_graph.subst_list:
            raise EmptyWordSubstance()

        self._check_morpheme(self.subst_nodes)
        self._check_morpheme(self.attr_nodes)

