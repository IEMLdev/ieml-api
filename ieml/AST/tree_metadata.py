from ieml.exceptions import DBNotSet


def needs_db(method):
    def wrapper(*args, **kwargs):
        if args[0]._db_connector is None:
            raise DBNotSet("DB not set but required for metadata retrieving") # DB not set error
        else:
            return method(*args, **kwargs)
    return wrapper


class TreeElementMetadata:

    _db_connector = None

    def __init__(self, element_ref):
        self.element_ref = element_ref
        self.db_entry = None
        self._retrieve_from_db()

    def __getitem__(self, item):
        pass

    @needs_db
    def __getitem__(self, item):
        return self.db_entry[item]

    @needs_db
    def __contains__(self, item):
        return item in self.db_entry

    def _retrieve_from_db(self):
        pass

    @classmethod
    def set_connector(cls, connector_instance):
        cls._db_connector = connector_instance


class TermMetadata(TreeElementMetadata):
    @needs_db
    def _retrieve_from_db(self):
        self.db_entry = self._db_connector.exact_ieml_term_search_noformat(self.element_ref.ieml)


class PropositionMetadata(TreeElementMetadata):
    """Class in charge of storing and retrieving metadata for an instance of an AbstractProposition"""


class ClosedPropositionMetadata(PropositionMetadata):

    @needs_db
    def _retrieve_from_db(self):
        self.db_entry = self._db_connector.exact_ieml_search(self.element_ref)


class NonClosedPropositionMetadata(PropositionMetadata):
    pass


class TextMetadata(TreeElementMetadata):
    @needs_db
    def _retrieve_from_db(self):
        self.db_entry = self._db_connector.get_text_from_ieml(self.element_ref)


class HypertextMetadata(TreeElementMetadata):
    @needs_db
    def _retrieve_from_db(self):
        self.db_entry = self._db_connector.get_hypertext_from_ieml(self.element_ref)