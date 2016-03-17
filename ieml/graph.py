import numpy as np


class Vertice:
    """Stores the representation of a vertice between nodes"""

    def __init__(self, node_subst, node_attr, node_mode):
        self.subst = node_subst
        self.attr = node_attr
        self.mode = node_mode

class AbstractNode:

    def is_connected_to(self, node):
        pass

class NullNode(AbstractNode):

    def is_connected_to(self, node):
        return False

class Node(AbstractNode):
    """A graph Node"""

    def __init__(self, node_id, ieml):
        """
        :param node_id: an integer representing the node's ID in the graph
        """
        self.id = node_id
        self.ieml = ieml
        self.vertices_list = []
        self.connected_to = []

    def add_vertice(self, to, mode):
        """
        Adds a connection (an IEML multiplication operation) to another node
        :param to: another node object
        :param mode: another node object
        """

        self.vertices_list.append(Vertice(self, to, mode))
        self.connected_to.append(to)

    def is_connected_to(self, node):
        return node in self.connected_to



class Graph:
    """Stores a representation of the graph described in the visual web interface"""

    def __init__(self, nodes_table):

        # the nodes table object stores the nodes_id -> nodes ieml name correpsondance
        self.nodes_table = {}
        for node in nodes_table:
            # if it's a "nullnode", we're storing it it a a special node
            if node["ieml_string"] is None:
                self.nodes_table[node["id"]] = NullNode()
            else:
                self.nodes_table[node["id"]] = Node(nodes_table["id"], node["ieml_string"])

        self.nodes_matrix = None # matrix representation of the graph for simpler searches
        self.graph_nodes_set = set() # set of nodes objects
        self.adjacency_matrix = None

    def add_vertice(self, subst_id, attr_id, mode_id):
        """Adds a AxBxC connection to the graph"""
        self.nodes_table[subst_id].add_vertice(self.nodes_table[attr_id],
                                               self.nodes_table[mode_id])
        # adding to the node_list the nodes that are attr and subst
        self.graph_nodes_set.add(self.nodes_table[subst_id])
        self.graph_nodes_set.add(self.nodes_table[attr_id])

    def _build_graph_nodes_list(self):
        """Converts the graph nodes set to a list so it's indexable"""
        self.graph_nodes_list = list(self.graph_nodes_set)

    def _build_adjacency_matrix(self):
        """Once the graph is fully built, this function is called to build the adjacency matrix"""

        self.adjacency_matrix = np.zeros((len(self.graph_nodes_set), len(self.graph_nodes_set)), dtype=bool)
        for (x,y), cell in np.ndenumerate(self.adjacency_matrix):
            # A cell is true if node x -> node y, else it's false
            self.adjacency_matrix[x][y] = self.graph_nodes_list[x].is_connected_to(self.graph_nodes_list[y])

    def check_graph(self, graph_checker):
        pass


class InvalidPropositionGraph(Exception):
    pass

class NoRootNodeFound(InvalidPropositionGraph):
    pass

class SeveralRootNodeFound(InvalidPropositionGraph):
    pass

class RegularGraphChecker:
    """Takes care of checking if a graph describing an IEMl proposition respects the IEML structura
    rules """

    def __init__(self, adjacency_matrix):
        self.adjacency_matrix = adjacency_matrix
        self.node_count = self.adjacency_matrix.shape[0]


    def _check_has_unique_root(self):
        """Using the adjacency matrix, checks that the graph has a unique root"""
        prod = np.dot(self.adjacency_matrix.transpose(), np.zeros(self.node_count, dtype=bool))
        #checking the "root count"
        root_count = np.dot(prod.astype(dtype=int), prod.astype(dtype=int))
        if root_count == 0: # only one root
            raise NoRootNodeFound()
        elif root_count > 1:# more than one root
            raise SeveralRootNodeFound()

    def _check_only_one_parent(self):
        pass


