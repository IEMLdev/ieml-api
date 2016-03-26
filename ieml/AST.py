import logging

class LoggedInstantiator(type):
    def __call__(cls, *args, **kwargs):
        logging.debug("Created a %s instance" % cls.__name__)
        # we need to call type.__new__ to complete the initialization
        return super(LoggedInstantiator, cls).__call__(*args, **kwargs)

class AbstractProposition(metaclass=LoggedInstantiator):
    # these are used for the proposition rendering
    times_symbol = "*"
    left_parent_symbol = "("
    right_parent_symbol = ")"
    plus_symbol = "+"
    left_bracket_symbol = "["
    right_bracket_symbol = "]"

class AbstractAdditiveProposition(AbstractProposition):

    def __init__(self, child_elements):
        self.childs = child_elements

    def __str__(self):
        return self.left_bracket_symbol + \
               self.plus_symbol.join([str(element) for element in self.childs]) + \
               self.right_bracket_symbol


class AbstractMultiplicativeProposition(AbstractProposition):

    def __init__(self, child_subst, child_attr=None, child_mode=None):
        self.subst = child_subst
        self.attr = child_attr
        self.mode = child_mode

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


class Word(AbstractMultiplicativeProposition):

    def __init__(self, child_subst, child_mode=None):
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

    def __str__(self):
        return "[" + self.ieml + "]"