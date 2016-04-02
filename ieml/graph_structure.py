import numpy as np

from ieml.AST import Term, Morpheme, Word, Clause, Sentence, SuperSentence, SuperClause
from .exceptions import InvalidNodeIEMLLevel
from .parsing import PropositionsParser


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

    def __init__(self, primitive_type):
        self.ast_type = primitive_type

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
        self._ast = None
        self.vertices_list = []
        self.connected_to = []

    def add_vertice(self, to, mode):
        """
        Adds a connection (an IEML multiplication operation) to another node
        :param to: another node object
        :param mode: another node object
        """
        new_vertice = Vertice(self, to, mode)
        self.vertices_list.append(new_vertice)
        self.connected_to.append(to)
        return new_vertice

    def is_connected_to(self, node):
        return node in self.connected_to

    @property
    def ast(self):
        """This is a getter, so the AST is generated only at the right time, for error handling"""
        if not self._ast:
            self._ast = PropositionsParser().parse(self.ieml)
        return self._ast

class GenericGraph:

    def to_ast(self):
        """Returns the AST corresponding to the graph"""
        pass

    def validate(self, graph_checker):
        """Verifies that the graph conforms to the IEML specifications and returns the
        corresponding IEML string if it's the case"""
        pass



class PropositionGraph(GenericGraph):
    """Stores a representation of the graph described in the visual web interface"""

    _primitive_type = None
    _multiplicative_type = None
    _additive_type = None

    def __init__(self, nodes_table):
        # the nodes table object stores the nodes_id -> nodes ieml name correpsondance
        self.nodes_table = {}
        for node in nodes_table:
            # if it's a "nullnode", we're storing it it a a special node
            if node["ieml_string"] is None:
                self.nodes_table[node["id"]] = NullNode(self._primitive_type)
            else:
                self.nodes_table[node["id"]] = Node(nodes_table["id"], node["ieml_string"])

        self.vertices_list = []
        self.nodes_matrix = None # matrix representation of the graph for simpler searches
        self.graph_nodes_set = set() # set of nodes objects
        self.adjacency_matrix = None


    def add_vertice(self, subst_id, attr_id, mode_id):
        """Adds a AxBxC connection to the graph"""
        new_vertice = self.nodes_table[subst_id].add_vertice(self.nodes_table[attr_id],
                                                             self.nodes_table[mode_id])
        self.vertices_list.append(new_vertice)
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

    def to_ast(self):
        # basically, we feed each child node to the parser, check if its the right primitive type,
        # and then build the AST "a la mano"
        for node in self.nodes_table.values():
            if not isinstance(node.ast, self._primitive_type):
                InvalidNodeIEMLLevel(node.id)

        # transforming the vertices into clauses or super_clauses
        multipicative_elements = [self._multiplicative_type(vertice.subst.ast,
                                                            vertice.attr.ast,
                                                            vertice.mode.ast)
                                  for vertice in self.vertices_list]

        # then returning the sentence/supersentence
        return self._additive_type(multipicative_elements)


class SentenceGraph(PropositionGraph):

    _primitive_type = Word
    _multiplicative_type = Clause
    _additive_type = Sentence


class SuperSentenceGraph(PropositionGraph):

    _primitive_type = Sentence
    _multiplicative_type = SuperClause
    _additive_type = SuperSentence

class WordsGraph(GenericGraph):
    """Graph reprensenting a word. Since the graph reprensenting a word doesn't have anything to do with the graph used for
    sentences and super-sentences, it doesn' inherit the Graph Class"""

    def __init__(self, nodes_table, subst_list, mode_list):

        self.nodes_table = {}
        # there aren't any nullnodes here
        for node in nodes_table:
            self.nodes_table[node["id"]] = Node(nodes_table["id"], node["ieml_string"])

        self.subst_list = [self.nodes_table[node_id] for node_id in subst_list]
        self.mode_list = [self.nodes_table[node_id] for node_id in mode_list]

    def validate(self, word_graph_checker):
        word_graph_checker().check(self)

    def to_ast(self):
        # basically, we feed each child node to the parser, check if it's a term,
        # and then build the AST "a la mano"
        for node in self.nodes_table.values():
            if not isinstance(node.ast, Term):
                InvalidNodeIEMLLevel(node.id)

        # Building the two morphemes for substance and attribute
        substance_morpheme = Morpheme([node.ast for node in self.subst_list])
        mode_morpheme = Morpheme([node.ast for node in self.mode_list])

        # then returning the word element
        return Word(substance_morpheme, mode_morpheme)

