import logging
from  functools import total_ordering
from helpers import LoggedInstantiator, Singleton
from models import DictionnaryQueries
from ieml.exceptions import IEMLTermNotFoundInDictionnary, IndistintiveTermsExist, InvalidConstructorParameter, \
    InvalidClauseComparison, TermComparisonFailed
from .propositional_graph import PropositionGraph


class TermsQueries(DictionnaryQueries, metaclass=Singleton):
    """A DB connector singleton class used by terms to prevent the number
    of DictionnaryQueries class instances from exploding"""
    pass


class ClosedProposition:
    """Interface class added to propositions that can be closed to be used in a USL
    These propositions, even if they're not truly closed in the script, are the only one
    that can link to USL's"""
    def __init__(self):
        self.hyperlink = []

    def add_hyperlink_list(self, usl_list):
        self.hyperlink += usl_list


class NonClosedProposition:
    """This class acts as an interface for propositions that *cannot* be closed"""
    pass

@total_ordering
class AbstractPropositionMetaclass(LoggedInstantiator):

    def __gt__(self, other):
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) > child_list.index(other)

    def __lt__(self, other):
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) < child_list.index(other)


class AbstractProposition(metaclass=AbstractPropositionMetaclass):
    # these are used for the proposition rendering
    times_symbol = "*"
    left_parent_symbol = "("
    right_parent_symbol = ")"
    plus_symbol = "+"
    left_bracket_symbol = "["
    right_bracket_symbol = "]"

    def __init__(self):
        self.childs = None # will be an iterable (list or tuple)
        self._has_been_checked = False
        self._ieml_string = None

    def __eq__(self, other):
        """Two propositions are equal if their childs'list or tuple are equal"""
        return self.childs == other.childs

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __str__(self):
        if not self._has_been_checked:
            logging.warning("Proposition %s hasn't been checked for ordering and consistency" % type(self))


    def check(self):
        """Checks the IEML validity of the IEML proposition"""
        for child in self.childs:
            child.check()

    def _gather_child_links(self):
        return [couple for sublist in [child.gather_hyperlinks() for child in self.childs]
                for couple in sublist]

    def is_ordered(self):
        pass

    def order(self):
        pass


class AbstractAdditiveProposition(AbstractProposition):

    def __init__(self, child_elements):
        super().__init__()
        # for convenience, it's possible to input a single element which is automatically converted into a list
        if isinstance(child_elements, list):
            self.childs = child_elements
        elif isinstance(child_elements, AbstractProposition) or isinstance(child_elements, Term):
            self.childs = [child_elements]
        else:
            raise InvalidConstructorParameter(self)

    def __str__(self):
        super().__str__()

        return self.left_bracket_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_bracket_symbol


class AbstractMultiplicativeProposition(AbstractProposition):

    def __init__(self, child_subst, child_attr=None, child_mode=None):
        super().__init__()
        self.subst = child_subst
        self.attr = child_attr
        self.mode = child_mode
        self.childs = (self.subst, self.attr, self.mode)

    def __str__(self):
        super().__str__()

        return self.left_parent_symbol + \
               str(self.subst) + self.times_symbol + \
               str(self.attr) + self.times_symbol + \
               str(self.mode) + self.right_parent_symbol

    def check(self):
        for child in self.childs:
            child.check()
            if not child.is_ordered():
                logging.warning("Additive proposition %s is not ordered, ordering it now" % str(child))
                child.order()

@total_ordering
class Morpheme(AbstractAdditiveProposition, NonClosedProposition):

    def __str__(self):
        super().__str__()

        return self.left_parent_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_parent_symbol

    def __gt__(self, other):
        max_length = max(len(self.childs), len(other.childs))
        for i in range(max_length):
            if len(self.childs) <= i: # this morpheme is a suffix of the other one, it's "smaller"
                return False
            elif len(other.childs) <= i: # the morpheme is a suffix of the current one, so current one is "bigger"
                return True
            else:
                if self.childs[i] != other.childs[i]:
                    return self.childs[i] > other.childs[i]

    def check(self):
        # first, we "ask" all the terms to check themselves through the parent method
        super().check()
        # then we check the terms for unicity by turning them into a set
        if len(self.childs) != len(set(self.childs)):
            raise IndistintiveTermsExist("There are %i indistinct terms. "
                                         % (len(self.childs) - len(set(self.childs))))
        # TODO : more checking
        # - term intersection
        # - paradigmatic intersection
        # - term number
        self._has_been_checked = True


    def is_ordered(self):
        """Returns true if its list of childs are sorted"""
        for i in range(len(self.childs)-1):
            if not self.childs[i] <= self.childs[i+1]:
                return False

        return True

    def order(self):
        """Orders the terms"""
        # terms have the TotalOrder decorator, as such, they can be automatically ordered
        self.childs.sort()


@total_ordering
class Word(AbstractMultiplicativeProposition, ClosedProposition):

    def __init__(self, child_subst, child_mode=None):
        super().__init__(child_subst)
        self.subst = child_subst
        self.mode = child_mode
        if self.mode is None:
            self.childs = (self.subst,)
        else:
            self.childs = (self.subst, self.mode)

    def __str__(self):
        if self.mode is None:
            return self.left_bracket_symbol + \
                   str(self.subst) +\
                   self.right_bracket_symbol
        else:
            return self.left_bracket_symbol + \
                   str(self.subst) + self.times_symbol + \
                   str(self.mode) + self.right_bracket_symbol

    def __gt__(self, other):
        if self.subst != other.subst:
            return self.subst > other.subst
        else:
            return self.mode > other.mode

    def gather_hyperlinks(self):
        # since morphemes cannot have hyperlinks, we don't gather links for the underlying childs
        return [(self, usl_ref) for usl_ref in self.hyperlink]




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
                raise InvalidClauseComparison()

    def gather_hyperlinks(self):
        return self._gather_child_links()




class Clause(AbstractClause):

    def check(self):
        # Clause won't ask for an underlying proposition to order itself, since the underlying
        # element is a word (which cannot be ordered)
        for child in self.childs:
            child.check()


class SuperClause(AbstractClause):
    pass


class AbstractSentence(AbstractAdditiveProposition, ClosedProposition):

    def __init__(self, child_elements):
        super().__init__(child_elements)
        self.graph = None

    def gather_hyperlinks(self):
        # first we build the (object, usl) tuple list for the current object
        links_list = [(self, usl_ref) for usl_ref in self.hyperlink]
        # then we add the hyperlinks from the child elements
        return links_list + self._gather_child_links()

    def check(self):
        # first, we call the parent method, which, by calling the check methods on clauses or superclauses,
        # ensures that the child elements are well ordered (especially the terms, or the underlying sentence)
        super().check()

        if len(self.childs) != 1:
            # then, we build the (super)sentence's graph using the (super)clause list
            self.graph = PropositionGraph(self.childs)
            self.graph.check() #the graph does some checking

        self._has_been_checked = True

    def order(self):
        """Orders the clauses/superclauses inside the sentence/supersentence, using the graph"""
        if self.graph is not None:
            self.childs = self.graph.get_ordereded_clauses_list()
        else:
            raise Exception()


class Sentence(AbstractSentence):

    def __init__(self, child_elements):
        super().__init__(child_elements)
        self.graph = None


class SuperSentence(AbstractSentence):

    def __init__(self, child_elements):
        super().__init__(child_elements)


@total_ordering
class Term(metaclass=AbstractPropositionMetaclass):

    def __init__(self, ieml_string):
        self.ieml = ieml_string
        self.objectid = None
        self.canonical_forms = None

    def __str__(self):
        return "[" + self.ieml + "]"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.objectid.__hash__()

    def __eq__(self, other):
        return self.objectid == other.objectid and self.objectid is not None

    def __gt__(self, other):
        # we use the DB's canonical forms
        # if the term has MORE canonical sequences, it's "BIGGER", so GT is TRUE
        if len(self.canonical_forms) > len(other.canonical_forms):
            return True
        else: # else, we have to compare sequences using the regular aphabetical order
            for i, seq in enumerate(self.canonical_forms):
                # for each sequence, if the sequences are different, we can return the comparison
                if self.canonical_forms[i] != other.canonical_forms[i]:
                    return self.canonical_forms[i] > other.canonical_forms[i]

        raise TermComparisonFailed(self.ieml, other.ieml)

    def check(self):
        """Checks that the term exists in the database, and if found, stores the terms's objectid"""
        result = TermsQueries().exact_ieml_term_search(self.ieml)
        try:
            self.objectid = result["_id"]
            self.canonical_forms = result["CANONICAL"]
        except TypeError:
            raise IEMLTermNotFoundInDictionnary(self.ieml)

