from ieml.ieml_objects.exceptions import TermNotFoundInDictionary
from ieml.ieml_objects.commons import IEMLObjects
from ieml.script.operator import script


class Term(IEMLObjects):
    def __init__(self, s):
        if isinstance(s, str) and s[0] == '[' and s[-1] == ']':
            s = s[1:-1]

        self.script = script(s)

        self.grammatical_class = self.script.script_class

        from models.terms.terms import TermsConnector
        term = TermsConnector().get_term(self.script)
        if term is None:
            raise TermNotFoundInDictionary(str(self.script))

        super().__init__([])

    __hash__ = IEMLObjects.__hash__

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return self.script == other.script

    def _do_gt(self, other):
        return self.script > other.script

    def _do_precompute_str(self):
        self._str = "[" + str(self.script) + "]"

    @property
    def empty(self):
        return self.script.empty

    @property
    def is_promotion(self):
        """This is kept as a property to keep homogeneity with the propositions"""
        return False

    def get_promotion_origin(self):
        return self
