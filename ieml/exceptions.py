
### Exception Raised by the commons (treescruture and proposition path)

class CommonsException(Exception):
    pass


class PropositionPathErrors(CommonsException):
    pass


class PathCannotBeEmpty(PropositionPathErrors):
    pass

### Exception raise by the Script


# class InvalidScriptForTableCreation(Exception):
#     pass


class InvalidScript(Exception):
    def __str__(self):
        return "Invalid arguments to create a parser."


class InvalidScriptCharacter(InvalidScript):
    def __init__(self, character):
        self.character = character

    def __str__(self):
        return 'Invalid character %s for a parser.'%str(self.character)


class IncompatiblesScriptsLayers(InvalidScript):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

    def __str__(self):
        return 'Unable to add the two scripts %s, %s they have incompatible layers.'%(str(self.s1), str(self.s2))


class NoRemarkableSiblingForAdditiveScript(Exception):
    pass
### These exeception are raised by the AST


class ASTException(Exception):
    pass


class TermException(ASTException):

    def __init__(self, terms_ieml):
        super().__init__()
        self.terms_ieml = terms_ieml


class IEMLTermNotFoundInDictionnary(TermException):

    def __str__(self):
        return "Cannot find term %s in the dictionnary" % self.terms_ieml


class TermComparisonFailed(TermException):
    def __init__(self, terms_ieml, other_terms_ieml):
        super().__init__(terms_ieml)
        self.other_term = other_terms_ieml

    def __str__(self):
        return "Comparison between term %s and %s failed" \
               % (self.terms_ieml, self.other_term)


class PropositionException(ASTException):
    def __init__(self, proposition_ref):
        super().__init__()
        self.proposition_ref = proposition_ref


class AdditiveOrderNotRespected(PropositionException):
    pass


class InvalidConstructorParameter(PropositionException):
    pass


class InvalidClauseComparison(PropositionException):

    def __init__(self, proposition_ref, other_ref):
        super().__init__(proposition_ref)
        self.other_ref = other_ref


class SentenceHasntBeenChecked(PropositionException):
    pass


class IndistintiveTermsExist(ASTException):
    pass


class TooManyTermsInMorpheme(ASTException):
    pass

### These exceptions /errors are graph_related


class InvalidPropositionGraph(ASTException):
    pass


class TooManyNodesInGraph(InvalidPropositionGraph):
    message = "Nodes limit in the graph exceeded"


class NoRootNodeFound(InvalidPropositionGraph):
    message = "Cannot find a root node for this graph"


class SeveralRootNodeFound(InvalidPropositionGraph):
    message = "Several root nodes exist for this graph"


class InvalidGraphNode(InvalidPropositionGraph):
    message = "%s"

    def __init__(self, node_id):
        super().__init__()
        self.node_id = node_id
        self.node_ieml = None

    def set_node_ieml(self, ieml):
        self.node_ieml = ieml

    def __str__(self):
        if self.node_ieml is not None:
            return self.message % self.node_ieml
        else:
            return self.message % str(self.node_id)


class NodeHasNoParent(InvalidGraphNode):
    message = "Node %s has no parent"


class InvalidNodeIEMLLevel(InvalidGraphNode):
    message = "Node %s doesn't have the right level to be used as a primitive for this level"


class NodeHasTooMuchParents(InvalidGraphNode):
    message = "Node %s has several parents"

### AST tools related errors


class ToolsException(Exception):
    pass


class CannotPromoteToLowerLevel(ToolsException):
    pass


class CannotRenderElementWithoutOrdering(ToolsException):
    pass


class CannotDemoteProposition(ToolsException):
    pass


class PropositionNotIncluded(ToolsException):
    pass

### Metadata exceptions


class MetadataException(Exception):
    pass


class CannotRetrieveMetadata(MetadataException):
    pass


class DBNotSet(MetadataException):
    pass

### USL exceptions ###


class USLException(Exception):
    pass


class InvalidPathException(USLException):
    pass


class OpenPropositionInTextException(USLException):
    pass


class EmptyTextException(USLException):
    pass

### Parser-related Errors


class ParserErrors(Exception):
    pass


class CannotParse(ParserErrors):
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return "Unable to parse the following string %s."%str(self.s)