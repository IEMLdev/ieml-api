from .base_queries import DBConnector
from .constants import PROPOSITION_COLLECTION
import ieml.AST


class PropositionsQueries(DBConnector):

    def __init__(self):
        super().__init__()
        self.propositions = self.db[PROPOSITION_COLLECTION]


    def _proposition_db_type(self, proposition):
        """Returns the DB name for a proposition"""
        return proposition.__class__.__name__.upper()

    def _retrieve_primitive_objectid(self, ieml_string, primitive_type):
        """Retrieves the objectid of an IEML primitive"""
        if primitive_type is ieml.AST.Term:
            return self.terms.find_one({"IEML" : ieml_string})["_id"]
        else:
            return self.propositions.find_one({"IEML" : ieml_string,
                                               "TYPE" : primitive_type.__name__.upper()})["_id"]

    def _retrieve_propositions_objectids(self, proposition_list):
        """Helper function to iterate through the list"""
        return [self._retrieve_primitive_objectid(str(proposition), type(proposition))
                for proposition in proposition_list]

    def _write_proposition_to_db(self, proposition, proposition_tags):
        """Saves a proposition to the db"""
        self.propositions.insert_one({"IEML" : str(proposition),
                                      "TYPE" : self._proposition_db_type(proposition),
                                      "TAGS" : proposition_tags})

    def save_closed_proposition(self, proposition_ast, proposition_tags):
        """Saves a valid proposition's AST into the database.
        A proposition being saved will always be a word, sentence or supersentence,
        As such, this function also saves the underlying primitives"""

        # for now, only does simple saving (whitout the Objectid matching stuff)
        # does check if the proposition is here or not beforehand though
        self._write_proposition_to_db(proposition_ast, proposition_tags)


