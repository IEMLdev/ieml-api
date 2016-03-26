import logging

class LoggedInstantiator(type):
    def __call__(cls, *args, **kwargs):
        logging.debug("Created a %s instance" % cls.__name__)
        # we need to call type.__new__ to complete the initialization
        return super(LoggedInstantiator, cls).__call__(*args, **kwargs)

class AbstractProposition(metaclass=LoggedInstantiator):
    pass


class AbstractAdditiveProposition(AbstractProposition):

    def __init__(self, child_elements):
        self.childs = child_elements


class AbstractMultiplicativeProposition(AbstractProposition):

    def __init__(self, child_subst, child_attr=None, child_mode=None):
        self.subst = child_subst
        self.attr = child_attr
        self.mode = child_mode


class Morpheme(AbstractAdditiveProposition):
    pass


class Word(AbstractMultiplicativeProposition):

    def __init__(self, child_subst, child_mode=None):
        self.subst = child_subst
        self.mode = child_mode


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