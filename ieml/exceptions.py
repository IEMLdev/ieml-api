
### Exception Raised by the commons (treescruture and proposition path)

class CommonsException(Exception):
    pass


class PropositionPathErrors(CommonsException):
    pass


class PathCannotBeEmpty(PropositionPathErrors):
    pass


### These exeception are raised by the AST


class ASTException(Exception):
    pass

class PropositionException(ASTException):
    pass


class AdditiveOrderNotRespected(PropositionException):
    pass


class InvalidConstructorParameter(PropositionException):
    pass


class InvalidClauseComparison(PropositionException):

    def __init__(self, proposition_ref, other_ref):
        super().__init__(proposition_ref)
        self.other_ref = other_ref


class IndistintiveTermsExist(ASTException):
    pass


class TooManyTermsInMorpheme(ASTException):
    pass

### These exceptions /errors are graph_related


class InvalidTree(ASTException):
    pass


class TooManyNodesInGraph(InvalidTree):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Nodes limit in the graph exceeded"


class NoRootNodeFound(InvalidTree):
    message = "Cannot find a root node for this graph"


class SeveralRootNodeFound(InvalidTree):
    message = "Several root nodes exist for this graph"


class NodeHasNoParent(InvalidTree):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "A node has no parent in the tree described by this object."


class InvalidNodeIEMLLevel(InvalidTree):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "A node doesn't have the right level to be used as a primitive for this level."


class NodeHasTooMuchParents(InvalidTree):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "A node a several parents in the tree described by this object."


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