from functools import total_ordering
from helpers import LoggedInstantiator, Singleton
from models import DictionaryQueries
from ieml.AST.constants import MAX_TERMS_IN_MORPHEME
from ieml.exceptions import IEMLTermNotFoundInDictionnary, IndistintiveTermsExist, InvalidConstructorParameter, \
    InvalidClauseComparison, TermComparisonFailed, SentenceHasntBeenChecked, TooManyTermsInMorpheme
from ieml.AST.propositional_graph import PropositionGraph
from ieml.AST.utils import PropositionPath, TreeStructure


class TermsQueries(DictionaryQueries, metaclass=Singleton):
    """A DB connector singleton class used by terms to prevent the number
    of DictionnaryQueries class instances from exploding"""
    pass


class ClosedProposition:
    """Interface class added to propositions that can be closed to be used in a USL
    These propositions, even if they're not truly closed in the script, are the only one
    that can link to USL's"""
    def __init__(self):
        super().__init__()
        self.hyperlink = []

    def add_hyperlink_list(self, usl_list):
        self.hyperlink += usl_list

    def _str_hyperlink(self):
        return ''.join(map(str, self.hyperlink))

    def get_closed_childs(self):
        """Returns only the child closed propositions of a closed proposition,
        e.g, words for a sentence, or sentences for a super-sentence"""
        # TODO : might be optimized, since this set is basically already computed in the proposition graph
        return set(subchild for child in self.childs for subchild in child.childs)


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


class AbstractProposition(TreeStructure, metaclass=AbstractPropositionMetaclass):
    # these are used for the proposition rendering
    times_symbol = "*"
    left_parent_symbol = "("
    right_parent_symbol = ")"
    plus_symbol = "+"
    left_bracket_symbol = "["
    right_bracket_symbol = "]"

    def __init__(self):
        super().__init__()

    def _gather_child_links(self, current_path):
        path = current_path + [self]
        return [couple for sublist in [child.gather_hyperlinks(path) for child in self.childs]
                for couple in sublist]

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(str, hyperlinks[current_path]))

        return result

    def __contains__(self, proposition):
        """Tests if the input proposition is contained in the current one, or in one of its child"""
        if proposition.__class__ < self.__class__:
            # first testing if it's one of the child
            for child in self.childs:
                if proposition == child:
                    return True
            # then testing if it's contained in one of the child
            for child in self.childs:
                if proposition in child:
                    return True
            # contained nowhere!
            return False
        else:
            # can't be contained if the level is higher
            return False


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

    def _do_precompute_str(self):
        self._str = self.left_bracket_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_bracket_symbol

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

    def _do_render_hyperlinks(self, hyperlinks, path):
        return self.left_bracket_symbol + \
               self.plus_symbol.join([element.render_hyperlinks(hyperlinks, path) for element in self.childs]) + \
               self.right_bracket_symbol


class AbstractMultiplicativeProposition(AbstractProposition):

    def __init__(self, child_subst, child_attr=None, child_mode=None):
        super().__init__()
        self.subst = child_subst
        self.attr = child_attr
        self.mode = child_mode
        self.childs = (self.subst, self.attr, self.mode)

    def _do_render_hyperlinks(self, hyperlinks, path):
        return self.left_parent_symbol + \
               self.subst.render_hyperlinks(hyperlinks, path) + self.times_symbol + \
               self.attr.render_hyperlinks(hyperlinks, path) + self.times_symbol + \
               self.mode.render_hyperlinks(hyperlinks, path) + self.right_parent_symbol

    def _do_precompute_str(self):
        self._str = self.left_parent_symbol + \
               str(self.subst) + self.times_symbol + \
               str(self.attr) + self.times_symbol + \
               str(self.mode) + self.right_parent_symbol


@total_ordering
class Morpheme(AbstractAdditiveProposition, NonClosedProposition):

    def _do_precompute_str(self):
       self._str = self.left_parent_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_parent_symbol

    def _do_checking(self):
        # then we check the terms for unicity by turning them into a set
        if len(self.childs) != len(set(self.childs)):
            raise IndistintiveTermsExist("There are %i indistinct terms. "
                                         % (len(self.childs) - len(set(self.childs))))

        if len(self.childs) > MAX_TERMS_IN_MORPHEME:
            raise TooManyTermsInMorpheme()

        # TODO : more checking
        # - term intersection
        # - paradigmatic intersection

    def _do_ordering(self):
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

    def _do_render_hyperlinks(self, hyperlinks, path):
        if self.mode is None:
            result = self.left_bracket_symbol + \
                     self.subst.render_hyperlinks(hyperlinks, path) + \
                     self.right_bracket_symbol
        else:
            result = self.left_bracket_symbol + \
                     self.subst.render_hyperlinks(hyperlinks, path) + self.times_symbol + \
                     self.mode.render_hyperlinks(hyperlinks, path) + self.right_bracket_symbol
        return result

    def _do_precompute_str(self):
        if self.mode is None:
            self._str = self.left_bracket_symbol + \
                   str(self.subst) +\
                   self.right_bracket_symbol
        else:
            self._str = self.left_bracket_symbol + \
                   str(self.subst) + self.times_symbol + \
                   str(self.mode) + self.right_bracket_symbol

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
        # since morphemes cannot have hyperlinks, we don't gather links for the underlying childs
        return [(PropositionPath(current_path, self), usl_ref) for usl_ref in self.hyperlink]

    def get_closed_childs(self):
        pass


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
        if len(self.childs) != 1:
            # then, we build the (super)sentence's graph using the (super)clause list
            self.graph = PropositionGraph(self.childs)
            self.graph.check() #the graph does some checking

    def _do_ordering(self):
        """Orders the clauses/superclauses inside the sentence/supersentence, using the graph"""
        if self._has_been_checked:
            if len(self.childs) != 1:
                self.childs = self.graph.get_ordereded_clauses_list()
        else:
            raise SentenceHasntBeenChecked(self)


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

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(str, hyperlinks[str(current_path)]))

        return result

    def _do_render_hyperlinks(self, hyperlinks, path):
        return "[" + self.ieml + "]"

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

    def check(self):
        """Checks that the term exists in the database, and if found, stores the terms's objectid"""
        result = TermsQueries().exact_ieml_term_search(self.ieml)
        try:
            self.objectid = result["_id"]
            self.canonical_forms = result["CANONICAL"]
        except TypeError:
            raise IEMLTermNotFoundInDictionnary(self.ieml)

    def order(self):
        pass
