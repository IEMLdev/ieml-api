from functools import total_ordering

from .commons import PropositionPath, AbstractPropositionMetaclass
from .tree_metadata import TermMetadata
from ieml.exceptions import TermComparisonFailed, CannotRetrieveMetadata, IEMLTermNotFoundInDictionnary


@total_ordering
class Term(metaclass=AbstractPropositionMetaclass):

    def __init__(self, ieml_string):
        if ieml_string[0] == '[' and ieml_string[-1] == ']':
            self.ieml = ieml_string[1:-1]
        else:
            self.ieml = ieml_string

        self.objectid = None
        self.canonical = None
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
        if len(self.canonical) != len(other.canonical):
            return len(self.canonical) > len(other.canonical)

        else: # else, we have to compare sequences using the regular aphabetical order
            for i, seq in enumerate(self.canonical):
                # for each sequence, if the sequences are different, we can return the comparison
                if self.canonical[i] != other.canonical[i]:
                    return self.canonical[i] > other.canonical[i]

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
                raise CannotRetrieveMetadata("Cannot retrieve metadata for term %s" % self.ieml)
        else:
            return self._metadata

    @property
    def is_promotion(self):
        """This is kept as a property to keep homogeneity with the propositions"""
        return False

    def _retrieve_metadata_instance(self):
        return TermMetadata(self)

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(lambda e: "<" + str(e[0]) + ">" + str(e[1]), hyperlinks[current_path]))

        return result

    def _do_render_hyperlinks(self, hyperlinks, path):
        return "[" + self.ieml + "]"

    def check(self):
        """Checks that the term exists in the database, and if found, stores the terms's objectid"""
        from models.base_queries import DictionaryQueries
        TermMetadata.set_connector(DictionaryQueries())
        try:
            self.objectid = self.metadata["OBJECT_ID"]
            self.canonical = self.metadata["CANONICAL"]
        except TypeError:
            raise IEMLTermNotFoundInDictionnary(self.ieml)

    def order(self):
        pass

    def get_promotion_origin(self):
        return self