import logging
from helpers import LoggedInstantiator, Singleton
from models import DictionnaryQueries
from .exceptions import IEMLTermNotFoundInDictionnary, IndistintiveTermsExist

class TermsQueries(DictionnaryQueries, metaclass=Singleton):
    """A DB connector singleton class used by terms to prevent the number
    of DictionnaryQueries class instances from exploding"""
    pass


class AbstractProposition(metaclass=LoggedInstantiator):
    # these are used for the proposition rendering
    times_symbol = "*"
    left_parent_symbol = "("
    right_parent_symbol = ")"
    plus_symbol = "+"
    left_bracket_symbol = "["
    right_bracket_symbol = "]"

    def __init__(self):
        self.childs = None # will be an iterable (list or tuple)

    def check(self):
        """Checks the IEML validity of the IEML proposition"""
        for child in self.childs:
            child.check()

class AbstractAdditiveProposition(AbstractProposition):

    def __init__(self, child_elements):
        super().__init__()
        self.childs = child_elements

    def __str__(self):
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
        return self.left_parent_symbol + \
               str(self.subst) + self.times_symbol + \
               str(self.attr) + self.times_symbol + \
               str(self.mode) + self.right_parent_symbol


class Morpheme(AbstractAdditiveProposition):

    def __str__(self):
        return self.left_parent_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_parent_symbol

    def check(self):
        # first, we "ask" all the terms to check themselves through the parent method
        super().check()
        # then we check the terms for unicity turning their objectid's into a set
        terms_objectids_list = [term.objectid for term in self.childs]
        if len(terms_objectids_list) != len(set([node.id for node in terms_objectids_list])):
            raise IndistintiveTermsExist()



class Word(AbstractMultiplicativeProposition):

    def __init__(self, child_subst, child_mode=None):
        super().__init__()
        self.subst = child_subst
        self.mode = child_mode

    def __str__(self):
        if self.mode is None:
            return self.left_bracket_symbol + \
                   str(self.subst) +\
                   self.right_bracket_symbol
        else:
            return self.left_bracket_symbol + \
                   str(self.subst) + self.times_symbol + \
                   str(self.mode) + self.right_bracket_symbol

class Clause(AbstractMultiplicativeProposition):
    pass


class Sentence(AbstractAdditiveProposition):
    pass


class SuperClause(AbstractMultiplicativeProposition):
    pass


class SuperSentence(AbstractAdditiveProposition):
    pass

class Term(metaclass=LoggedInstantiator):

    def __init__(self, ieml_string):
        self.ieml = ieml_string
        self.objectid = None

    def __str__(self):
        return "[" + self.ieml + "]"

    def check(self):
        """Checks that the term exists in the database, and if found, stores the terms's objectid"""
        # TODO : optimize this code :
        # for now, since I don't know how to do exact text queries in MongoDB,
        # i'm retrieving the list of ALL mathing IEML strings and then checking if the
        # self.ieml string is in the list
        query_result_list = TermsQueries().search_for_ieml_terms(self.ieml)
        try:
            index = query_result_list.index(self.ieml)
            self.objectid = query_result_list[index]["_id"]
        except ValueError:
            raise IEMLTermNotFoundInDictionnary(self.ieml)

