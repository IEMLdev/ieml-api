from functools import total_ordering

from .terms import Term
from .commons import PropositionPath, AbstractProposition
from .constants import MAX_TERMS_IN_MORPHEME
from .propositional_graph import PropositionGraph
from .tree_metadata import ClosedPropositionMetadata, NonClosedPropositionMetadata
from ieml.exceptions import IndistintiveTermsExist, InvalidConstructorParameter, \
    InvalidClauseComparison, SentenceHasntBeenChecked, TooManyTermsInMorpheme


class ClosedProposition:
    """Interface class added to propositions that can be closed to be used in a USL
    These propositions, even if they're not truly closed in the script, are the only one
    that can link to USL's"""
    def __init__(self):
        super().__init__()
        self.hyperlink = []
        self._is_promotion = None
        self._promoted_from = None # reference to the promoted proposition/term

    @property
    def is_promotion(self):
        if self._is_promotion is None:
            self._do_promotion_check()

        return self._is_promotion

    def _do_promotion_check(self):
        """This function checks if a closed proposition is a promotion of another,
        by simply checking if its elements are empty"""
        pass

    def get_promotion_origin(self):
        """Recursively goes down the AST to find the promotion's origin"""
        if self.is_promotion:
            return self._promoted_from.get_promotion_origin()
        else:
            return self

    def add_hyperlink_list(self, usl_list):
        # check that all literals are not None
        if any(map(lambda h: h[0] is not None, usl_list)):
            raise InvalidConstructorParameter()

        self.hyperlink += usl_list
    #
    # def _str_hyperlink(self):
    #     return ''.join(map(str, self.hyperlink))

    def _retrieve_metadata_instance(self):
        return ClosedPropositionMetadata(self)


class NonClosedProposition:
    """This class acts as an interface for propositions that *cannot* be closed"""
    def _retrieve_metadata_instance(self):
        return NonClosedPropositionMetadata(self)



class AbstractAdditiveProposition(AbstractProposition):

    def __init__(self, child_elements):
        super().__init__()
        # for convenience, it's possible to input a single element which is automatically converted into a list
        if isinstance(child_elements, list):
            self.children = child_elements
        elif isinstance(child_elements, AbstractProposition) or isinstance(child_elements, Term):
            self.children = [child_elements]
        else:
            raise InvalidConstructorParameter(self)

    @property
    def is_null(self):
        if len(self.children) == 1:
            return self.children[0].is_null
        else:
            return False

    def _do_precompute_str(self):
        self._str = self.RenderSymbols.left_bracket + \
                    self.RenderSymbols.plus.join([str(element) for element in self.children]) + \
                    self.RenderSymbols.right_bracket

    def __gt__(self, other):
        max_length = max(len(self.children), len(other.children))
        for i in range(max_length):
            if len(self.children) <= i: # this morpheme is a suffix of the other one, it's "smaller"
                return False
            elif len(other.children) <= i: # the morpheme is a suffix of the current one, so current one is "bigger"
                return True
            else:
                if self.children[i] != other.children[i]:
                    return self.children[i] > other.children[i]

    def _do_render_hyperlinks(self, hyperlinks, path):
        return self.RenderSymbols.left_bracket + \
               self.RenderSymbols.plus.join([element.render_hyperlinks(hyperlinks, path) for element in self.children])+\
               self.RenderSymbols.right_bracket


class AbstractMultiplicativeProposition(AbstractProposition):

    def __init__(self, child_subst, child_attr=None, child_mode=None):
        super().__init__()
        self.subst = child_subst
        self.attr = child_attr
        self.mode = child_mode
        self.children = (self.subst, self.attr, self.mode)

    def _do_render_hyperlinks(self, hyperlinks, path):
        return self.RenderSymbols.left_parent + \
               self.subst.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.times + \
               self.attr.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.times + \
               self.mode.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.right_parent

    def _do_precompute_str(self):
        self._str = self.RenderSymbols.left_parent + \
               str(self.subst) + self.RenderSymbols.times + \
               str(self.attr) + self.RenderSymbols.times + \
               str(self.mode) + self.RenderSymbols.right_parent


@total_ordering
class Morpheme(AbstractAdditiveProposition, NonClosedProposition):

    def _do_precompute_str(self):
        self._str = self.RenderSymbols.left_parent + \
                    self.RenderSymbols.plus.join([str(element) for element in self.children]) + \
                    self.RenderSymbols.right_parent

    def _do_render_hyperlinks(self, hyperlinks, path):
        return self.RenderSymbols.left_parent + \
               self.RenderSymbols.plus.join(
                   [element.render_hyperlinks(hyperlinks, path) for element in self.children]) + \
               self.RenderSymbols.right_parent

    def _do_checking(self):
        # then we check the terms for unicity by turning them into a set
        if len(self.children) != len(set(self.children)):
            raise IndistintiveTermsExist("There are %i indistinct terms. "
                                         % (len(self.children) - len(set(self.children))))

        if len(self.children) > MAX_TERMS_IN_MORPHEME:
            raise TooManyTermsInMorpheme()

        # TODO : more checking
        # - term intersection
        # - paradigmatic intersection

    def _do_ordering(self):
        """Orders the terms"""
        # terms have the TotalOrder decorator, as such, they can be automatically ordered
        self.children.sort()


@total_ordering
class Word(AbstractMultiplicativeProposition, ClosedProposition):

    def __init__(self, child_subst, child_mode=None):
        super().__init__(child_subst)
        self.subst = child_subst
        self.mode = child_mode
        if self.mode is None:
            self.children = (self.subst,)
        else:
            self.children = (self.subst, self.mode)

    @property
    def is_null(self):
        if self.mode is None:
            return self.subst.is_null
        else:
            return False

    def _do_promotion_check(self):
        if self.mode is None and len(self.subst.children) == 1:
            self._is_promotion = True
            self._promoted_from = self.subst.children[0]
        else:
            self._is_promotion = False

    def _do_render_hyperlinks(self, hyperlinks, path):
        if self.mode is None:
            result = self.RenderSymbols.left_bracket + \
                     self.subst.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.right_bracket
        else:
            result = self.RenderSymbols.left_bracket + \
                     self.subst.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.times + \
                     self.mode.render_hyperlinks(hyperlinks, path) + self.RenderSymbols.right_bracket
        return result

    def _do_precompute_str(self):
        if self.mode is None:
            self._str = self.RenderSymbols.left_bracket + \
                        str(self.subst) + \
                        self.RenderSymbols.right_bracket
        else:
            self._str = self.RenderSymbols.left_bracket + \
                        str(self.subst) + self.RenderSymbols.times + \
                        str(self.mode) + self.RenderSymbols.right_bracket

    def __gt__(self, other):
        if self.subst != other.subst:
            return self.subst > other.subst
        elif self.mode is not None:
            if other.mode is not None:
                return self.mode > other.mode
            else:
                return True
        else:
            return False

    def gather_hyperlinks(self, current_path):
        # since morphemes cannot have hyperlinks, we don't gather links for the underlying children
        return [(PropositionPath(current_path, self), usl_ref) for usl_ref in self.hyperlink]



@total_ordering
class AbstractClause(AbstractMultiplicativeProposition, NonClosedProposition):

    def __gt__(self, other):
        if self.subst != other.subst:
            # the comparison depends on the terms of the two substs
            return self.subst > other.subst
        else:
            if self.attr != other.attr:
                return self.attr > other.attr
            else:
                raise InvalidClauseComparison(self, other)
    @property
    def is_null(self):
        return self.subst.is_null and self.attr.is_null and self.mode.is_null

    def gather_hyperlinks(self, current_path):
        return self._gather_child_links(current_path)


class Clause(AbstractClause):
    pass


class SuperClause(AbstractClause):
    pass


@total_ordering
class AbstractSentence(AbstractAdditiveProposition, ClosedProposition):

    def __init__(self, child_elements):
        super().__init__(child_elements)
        self.graph = None

    def gather_hyperlinks(self, current_path):
        # first we build the (object, usl) tuple list for the current object
        links_list = [(PropositionPath(current_path, self), usl_ref) for usl_ref in self.hyperlink]
        # then we add the hyperlinks from the child elements
        return links_list + self._gather_child_links(current_path)

    def _do_checking(self):
        # if it's a single-clause list, no graph building
        if len(self.children) != 1:
            # then, we build the (super)sentence's graph using the (super)clause list
            self.graph = PropositionGraph(self.children)
            self.graph.check() #the graph does some checking

    def _do_ordering(self):
        """Orders the clauses/superclauses inside the sentence/supersentence, using the graph"""
        if self._has_been_checked:
            if len(self.children) != 1:
                self.children = self.graph.get_ordereded_clauses_list()
        else:
            raise SentenceHasntBeenChecked(self)

    def _do_promotion_check(self):
        if len(self.children) == 1 and self.children[0].mode.is_null and self.children[0].attr.is_null:
            self._is_promotion = True
            self._promoted_from = self.children[0].subst
        else:
            self._is_promotion = False


class Sentence(AbstractSentence):

    def __init__(self, child_elements):
        super().__init__(child_elements)


class SuperSentence(AbstractSentence):

    def __init__(self, child_elements):
        super().__init__(child_elements)


