from helpers import Singleton

class TreeElementMetadata:

    _db_connector = None

    def __init__(self, element_ieml):
        self.element_ieml = element_ieml
        self.db_entry = None

    def __getitem__(self, item):
        pass

    def _retrieve_from_db(self):
        pass

    @classmethod
    def set_connecto(cls, connector_instance):
        cls._db_connector = connector_instance

class PropositionMetadata(TreeElementMetadata):
    """Class in charge of storing and retrieving metadata for an instance of an AbstractProposition"""

    def __getitem__(self, item):
        if self.db_entry is None:
            self._retrieve_from_db()

        return self.db_entry[item]

    def _retrieve_from_db(self):
        if self.db_entry is None:
            self.db_entry = self._db_connector.exact_ieml_search(self.element_ieml)



class TextMetadata(TreeElementMetadata):
    pass


class HypertextMetadata(TreeElementMetadata):
    pass