def needs_db(method):
    def wrapper(*args, **kwargs):
        if args[0]._db_connector is None:
            raise Exception("DB not set but required for metadata retrieving") # DB not set error
        else:
            return method(*args, **kwargs)
    return wrapper


class TreeElementMetadata:

    _db_connector = None

    def __init__(self, element_ref):
        self.element_ref = element_ref
        self.db_entry = None

    def __getitem__(self, item):
        pass

    def _retrieve_from_db(self):
        pass

    @classmethod
    def set_connector(cls, connector_instance):
        cls._db_connector = connector_instance


class PropositionMetadata(TreeElementMetadata):
    """Class in charge of storing and retrieving metadata for an instance of an AbstractProposition"""


class ClosedPropositionMetadata(PropositionMetadata):

    def __init__(self, element_ref):
        super().__init__(element_ref)
        self._retrieve_from_db()

    @needs_db
    def __getitem__(self, item):
        return self.db_entry[item]

    @needs_db
    def __contains__(self, item):
        return item in self.db_entry

    @needs_db
    def _retrieve_from_db(self):
        self.db_entry = self._db_connector.exact_ieml_search(self.element_ref)


class NonClosedPropositionMetadata(PropositionMetadata):
    pass


class TextMetadata(TreeElementMetadata):
    pass


class HypertextMetadata(TreeElementMetadata):
    pass