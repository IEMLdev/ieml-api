from functools import total_ordering
from helpers import LoggedInstantiator
from ieml.AST.tree_metadata import ClosedPropositionMetadata, NonClosedPropositionMetadata, TermMetadata
from ieml.AST.constants import MAX_TERMS_IN_MORPHEME
from ieml.exceptions import IndistintiveTermsExist, InvalidConstructorParameter, \
    InvalidClauseComparison, TermComparisonFailed, SentenceHasntBeenChecked, TooManyTermsInMorpheme,\
    IEMLTermNotFoundInDictionnary
from ieml.AST.propositional_graph import PropositionGraph
from ieml.AST.utils import PropositionPath, TreeStructure

# class TermsQueries(DictionaryQueries, metaclass=Singleton):
#     """A DB connector singleton class used by terms to prevent the number
#     of DictionnaryQueries class instances from exploding"""
#     pass


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
        self.hyperlink += usl_list

    def _str_hyperlink(self):
        return ''.join(map(str, self.hyperlink))

    def _retrieve_metadata_instance(self):
        return ClosedPropositionMetadata(self)


class NonClosedProposition:
    """This class acts as an interface for propositions that *cannot* be closed"""
    def _retrieve_metadata_instance(self):
        return NonClosedPropositionMetadata(self)


@total_ordering
class AbstractPropositionMetaclass(LoggedInstantiator):
    """This metaclass enables the comparison of class times, such as (Sentence > Word) == True"""

    def __gt__(self, other):
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) > child_list.index(other)

    def __lt__(self, other):
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) < child_list.index(other)


class AbstractProposition(TreeStructure, metaclass=AbstractPropositionMetaclass):
    """This class is the parent class of all propositions, namely Morpheme, Word,
    Clause, Sentence, Superclause, Supersentence"""

    class RenderSymbols:
        """This class is just a container for the rendering symbols"""
        times = "*"
        left_parent = "("
        right_parent = ")"
        plus = "+"
        left_bracket = "["
        right_bracket = "]"

    def __init__(self):
        super().__init__()

    def __contains__(self, proposition):
        """Tests if the input proposition is contained in the current one, or in one of its child"""
        if proposition == self:
            return True
        else: # could be contained in the children proposition
            if proposition.__class__ < self.__class__:
                # testing if it's contained in one of the child
                for child in self.children:
                    if proposition in child:
                        return True
                # contained nowhere!
                return False
            else:
                # can't be contained if the level is higher
                return False

    def _gather_child_links(self, current_path):
        path = current_path + [self]
        return [couple for sublist in [child.gather_hyperlinks(path) for child in self.children]
                for couple in sublist]

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(str, hyperlinks[current_path]))

        return result




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
        self._str = self.RenderSymbols.left_bracket+ \
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
               self.RenderSymbols.plus.join([element.render_hyperlinks(hyperlinks, path) for element in self.children]) + \
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
                     self.subst.render_hyperlinks(hyperlinks, path) + \
                     self.RenderSymbols.right_bracket
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


@total_ordering
class Term(metaclass=AbstractPropositionMetaclass):

    def __init__(self, ieml_string):
        if ieml_string[0] == '[' and ieml_string[-1] == ']':
            self.ieml = ieml_string[1:-1]
        else:
            self.ieml = ieml_string

        self.objectid = None
        self.canonical_forms = None
        self._metadata = None

    def __str__(self):
        return "[" + self.ieml + "]"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.objectid.__hash__()

    def __eq__(self, other):
        if isinstance(other, Term):
            return self.objectid is not None and self.objectid == other.objectid
        else:
            return False

    def __contains__(self, proposition):
        return proposition == self

    def __gt__(self, other):
        # we use the DB's canonical forms
        # if the term has MORE canonical sequences, it's "BIGGER", so GT is TRUE
        if len(self.canonical_forms) != len(other.canonical_forms):
            return len(self.canonical_forms) > len(other.canonical_forms)

        else: # else, we have to compare sequences using the regular aphabetical order
            for i, seq in enumerate(self.canonical_forms):
                # for each sequence, if the sequences are different, we can return the comparison
                if self.canonical_forms[i] != other.canonical_forms[i]:
                    return self.canonical_forms[i] > other.canonical_forms[i]

        raise TermComparisonFailed(self.ieml, other.ieml)

    @property
    def is_null(self):
        null_term = Term("E:")
        null_term.check()
        return self == null_term

    @property
    def level(self):
        """Returns the string level of an IEML object, such as TEXT, WORD, SENTENCE, ..."""
        return self.__class__.__name__.upper()

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self._retrieve_metadata_instance()
            if self._metadata is not None:
                return self._metadata
            else:
                # TODO : define exception for this (when it's not possible to find the metadata)
                raise Exception("Cannot retrieve metadata for this element")
        else:
            return self._metadata

    def _retrieve_metadata_instance(self):
        return TermMetadata(self)

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(str, hyperlinks[current_path]))

        return result

    def _do_render_hyperlinks(self, hyperlinks, path):
        return "[" + self.ieml + "]"

    def check(self):
        """Checks that the term exists in the database, and if found, stores the terms's objectid"""
        from models.base_queries import DictionaryQueries
        TermMetadata.set_connector(DictionaryQueries())
        try:
            self.objectid = self.metadata["OBJECT_ID"]
            self.canonical_forms = self.metadata["CANONICAL"]
        except TypeError:
            raise IEMLTermNotFoundInDictionnary(self.ieml)

    def order(self):
        pass

    def get_promotion_origin(self):
        return self
