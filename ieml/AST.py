
class AbstractProposition:
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

class Term:

    def __init__(self, ieml_string):
        self.ieml = ieml_string