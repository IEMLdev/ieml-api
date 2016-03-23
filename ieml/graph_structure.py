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

class GenericGraph:

    def _render_ieml_sum(self, ):
        """Simple helper function that returns the IEML string for a sum of string"""
        return

    def _generate_ieml_string(self):
        """Generates the IEML string for the graph"""
        pass

    def validate(self, graph_checker, graph_renderer):
        """Verifies that the graph conforms to the IEML specifications and returns the
        corresponding IEML string if it's the case"""
        pass



class PropositionGraph(GenericGraph):
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

    def _generate_ieml_string(self):
        """Generates the IEML string for the graph"""
        pass


    def validate(self, proposition_graph_checker, proposition_graph_renderer):
        pass


class SentenceGraph(PropositionGraph):

    def generate_ieml_string(self):
        pass

class SuperSentenceGraph(PropositionGraph):
    pass

class WordsGraph:
    """Graph reprensenting a word. Since the graph reprensenting a word doesn't have anything to do with the graph used for
    sentences and super-sentences, it doesn' inherit the Graph Class"""

    def __init__(self, nodes_table, subst_list, attr_list):
        self.nodes_table = {}
        # there aren't any nullnodes here
        for node in nodes_table:
            self.nodes_table[node["id"]] = Node(nodes_table["id"], node["ieml_string"])

        self.subst_list = [self.nodes_table[node_id] for node_id in subst_list]
        self.attr_list = [self.nodes_table[node_id] for node_id in attr_list]

    def _generate_ieml_string(self, graph_renderer):
        """Returns the corresponding IEML string"""

        subst_sum_string = graph_renderer.render_sum([node.ieml for node in self.subst_list])
        if not self.attr_list:
            return graph_renderer.wrap_with_brackets(
                graph_renderer.wrap_with_parenthesis(
                    subst_sum_string
                )
            )
        else:
            attr_sum_string = graph_renderer.render_sum([node.ieml for node in self.attr_list])

            return graph_renderer.wrap_with_brackets(
                graph_renderer.render_product(
                    subst_sum_string, attr_sum_string
                )
            )

    def validate(self, word_graph_checker, word_graph_renderer):
        word_graph_checker().check(self)
        return self._generate_ieml_string(word_graph_renderer)


