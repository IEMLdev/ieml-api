from ieml.ieml_objects.exceptions import TermNotFoundInDictionary
from ieml.ieml_objects.commons import IEMLObjects
from ieml.script.operator import script


class Term(IEMLObjects):
    closable = True

    def __init__(self, s):
        if isinstance(s, str) and s[0] == '[' and s[-1] == ']':
            s = s[1:-1]

        if isinstance(s, Term):
            self.script = s.script
        else:
            self.script = script(s)

        self.grammatical_class = self.script.script_class

        from models.terms.terms import TermsConnector
        term = TermsConnector().get_term(self.script)
        if term is None:
            raise TermNotFoundInDictionary(str(self.script))

        super().__init__([])

        self._relations = {}

    def relations(self, relation_name):
        if relation_name not in self._relations:
            from models.relations import RelationsQueries
            self._relations[relation_name] = \
                [Term(s) for s in RelationsQueries.relations(self.script, relation_title=relation_name)]

        return self._relations[relation_name]


    __hash__ = IEMLObjects.__hash__

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return self.script == other.script

    def _do_gt(self, other):
        return self.script > other.script

    def compute_str(self, children_str):
        return "[" + str(self.script) + "]"

    @property
    def empty(self):
        return self.script.empty