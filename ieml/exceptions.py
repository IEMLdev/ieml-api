
### These exeception are raised by the AST

class ASTException(Exception):
    pass

class TermException(ASTException):

    def __init__(self, terms_ieml):
        super().__init__()
        self.terms_ieml = terms_ieml

class IEMLTermNotFoundInDictionnary(TermException):
    pass

class TermComparisonFailed(TermException):
    def __init__(self, terms_ieml, other_terms_ieml):
        super().__init__(terms_ieml)
        self.other_term = other_terms_ieml

class PropositionException(ASTException):
    def __init__(self, proposition_ref):
        super().__init__()
        self.proposition_ref = proposition_ref

class AdditiveOrderNotRespected(PropositionException):
    pass

class InvalidConstructorParameter(PropositionException):
    pass

class InvalidClauseComparison(PropositionException):
    pass


### These exceptions /errors are graph_related

class InvalidPropositionGraph(ASTException):
    pass


class InvalidWord(InvalidPropositionGraph):
    pass


class IndistintiveTermsExist(InvalidWord):
    pass


class EmptyWordSubstance(InvalidPropositionGraph):
    pass


class NoRootNodeFound(InvalidPropositionGraph):
    pass


class SeveralRootNodeFound(InvalidPropositionGraph):
    pass


class InvalidGraphNode(InvalidPropositionGraph):

    def __init__(self, node_id):
        super().__init__()
        self.node_id = node_id


class NodeHasNoParent(InvalidGraphNode):
    pass

class InvalidNodeIEMLLevel(InvalidGraphNode):
    pass

class NodeHasTooMuchParents(InvalidGraphNode):
    pass

### AST tools related errors

class ToolsException(Exception):
    pass

class CannotPromoteToLowerLevel(ToolsException):
    pass


### USL errors ###

class InvalidPathException(Exception):
    pass