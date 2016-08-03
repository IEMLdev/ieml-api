from ieml.AST.commons import AbstractProposition
from .tree_metadata import TermMetadata
from ieml.exceptions import TermComparisonFailed, CannotRetrieveMetadata, IEMLTermNotFoundInDictionnary
from ieml.parsing.script import ScriptParser
from ieml.script import Script
from models.terms.terms import TermsConnector


class Term(AbstractProposition):

    def __init__(self, script):
        super().__init__()
        self.children = []

        if isinstance(script, str):
            if script[0] == '[' and script[-1] == ']':
                script = script[1:-1]
            else:
                script = script
            self.script = ScriptParser().parse(script)
        elif isinstance(script, Script):
            self.script = script
        elif isinstance(script, Term):
            self.script = script.script
        else:
            raise ValueError

        self.grammatical_class = self.script.script_class

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False
        return self.script == other.script

    __hash__ = AbstractProposition.__hash__

    def __repr__(self):
        return str(self)

    def __gt__(self, other):
        return self.script > other.script

    def _do_precompute_str(self):
        self._str = "[" + str(self.script) + "]"

    def _do_checking(self):
        from models.base_queries import DictionaryQueries
        TermMetadata.set_connector(DictionaryQueries())

        term = TermsConnector().get_term(self.script)
        if term is None:
            raise IEMLTermNotFoundInDictionnary(str(self.script))

    def _do_ordering(self):
        pass

    @property
    def is_null(self):
        return self.script.empty

    @property
    def is_promotion(self):
        """This is kept as a property to keep homogeneity with the propositions"""
        return False

    def _retrieve_metadata_instance(self):
        return TermMetadata(self)

    def _do_render_hyperlinks(self, hyperlinks, path):
        return str(self)

    def get_promotion_origin(self):
        return self
