from ieml.exceptions import InvalidGraphNode
from ieml.ieml_objects.commons import IEMLObjects, TreeGraph
from ieml.ieml_objects.constants import MAX_NODES_IN_HYPERTEXT, MAX_DEPTH_IN_HYPERTEXT
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument
from ieml.ieml_objects.sentences import Sentence, SuperSentence
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word


class PropositionPath:
    def __init__(self, list_proposition):
        super().__init__()
        self.path = list_proposition

    def in_text(self, text):
        current = text
        for p in self.path:
            if not p in current.children:
                return False
            current = p
        return True

    @property
    def end(self):
        return self.path[-1]


class Hyperlink(IEMLObjects):
    def __init__(self, substance, attribute, mode):
        super().__init__()

        if not isinstance(substance, Text):
            raise InvalidIEMLObjectArgument(Hyperlink, "The substance %s must be a Text instance."%str(substance))

        if not isinstance(attribute, Text):
            raise InvalidIEMLObjectArgument(Hyperlink, "The attribute %s must be a Text instance."%str(substance))

        if substance == attribute:
            raise InvalidIEMLObjectArgument(Hyperlink, "The substance and the attribute %s must be distinct."%str(substance))

        if not isinstance(mode, PropositionPath):
            raise InvalidIEMLObjectArgument(Hyperlink, "The mode %s must be a PropositionPath instance."%str(substance))

        if not mode.in_text(substance):
            raise InvalidIEMLObjectArgument(Hyperlink, "The mode %s should be a PropositionPath in the text in"
                                                       " substance %s."%(str(mode), str(substance)))

        if not isinstance(mode.end, (Word, Sentence, SuperSentence)):
            raise InvalidIEMLObjectArgument(Hyperlink, "The mode %s must be a PropositionPath pointing to a Word, a "
                                                       "Sentence or a SuperSentence."%str(mode))

        self.children = (substance, attribute, mode)

class Hypertext(IEMLObjects):
    def __init__(self, hyperlink_list):
        super().__init__()

        try:
            _children = [e for e in hyperlink_list]
        except TypeError:
            raise InvalidIEMLObjectArgument(Hypertext, "The argument %s is not iterable."%str(hyperlink_list))

        if not all(isinstance(e, Hyperlink) for e in _children):
            raise InvalidIEMLObjectArgument(Hypertext, "The argument %s must be a list of Hyperlink instance."%
                                            str(_children))

        try:
            self.tree_graph = TreeGraph(((c[0], c[1], c) for c in _children))
        except InvalidGraphNode as e:
            raise InvalidIEMLObjectArgument(Hypertext, e.message)

        if len(self.tree_graph.nodes) > MAX_NODES_IN_HYPERTEXT:
            raise InvalidIEMLObjectArgument(Hypertext, "Too many text in this hypertext: %d>%d."%
                                            (len(self.tree_graph.nodes), MAX_NODES_IN_HYPERTEXT))

        if len(self.tree_graph.stages) > MAX_DEPTH_IN_HYPERTEXT:
            raise InvalidIEMLObjectArgument(Hypertext, "The depth of the tree graph of this hypertext is too big: %d>%d"
                                            %(len(self.tree_graph.stages), MAX_DEPTH_IN_HYPERTEXT))

        self.children = tuple(self.tree_graph.nodes)