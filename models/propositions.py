
from models.exceptions import PropositionAlreadyExists, ObjectTypeNotStoredinDB
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

    def retrieve_proposition_objectid(self, proposition):
        """Retrieves the objectid of an IEML primitive"""
        if isinstance(proposition,ieml.AST.Term):
            return self.terms.find_one({"_id" : proposition.ieml})["_id"]

        elif isinstance(proposition, (ieml.AST.Sentence, ieml.AST.Word, ieml.AST.SuperSentence)):
            return self.propositions.find_one({"_id" : str(proposition),
                                               "TYPE" : self._proposition_db_type(proposition)})["_id"]
        else:
            raise ObjectTypeNotStoredinDB()

    def _retrieve_propositions_objectids(self, proposition_list):
        """Helper function to iterate through the list"""
        return [self.retrieve_proposition_objectid(proposition)
                for proposition in proposition_list]

    def _write_proposition_to_db(self, proposition, proposition_tags):
        """Saves a proposition to the db"""
        self.propositions.insert_one({"_id" : str(proposition),
                                      "TYPE" : self._proposition_db_type(proposition),
                                      "TAGS" : {"FR" : proposition_tags["FR"],
                                                "EN" : proposition_tags["EN"]}})

    def save_closed_proposition(self, proposition_ast, proposition_tags):
        """Saves a valid proposition's AST into the database.
        A proposition being saved will always be a word, sentence or supersentence,
        As such, this function also saves the underlying primitives"""

        # for now, only does simple saving (whitout the Objectid matching stuff)
        # does check if the proposition is here or not beforehand though
        if self.propositions.find_one({"_id" : str(proposition_ast)}) is None:
            self._write_proposition_to_db(proposition_ast, proposition_tags)
        else:
            PropositionAlreadyExists()


    def search_for_propositions(self, search_string, max_level):

        if max_level == ieml.AST.Sentence:
            type_filter = {"$in": ["WORD", "SENTENCE"]}
        elif max_level == ieml.AST.SuperSentence:
            type_filter = {"$in": ["WORD", "SENTENCE", "SUPERSENTENCE"]}
        else:
            type_filter = "WORD"

        result = self.propositions.find({"$text" : {"$search" : search_string},
                                         "TYPE": type_filter},
                                        {"TAGS" : 1, "TYPE" : 1})

        return list(result)

    def exact_ieml_search(self, ieml_proposition):
        return self.propositions.find_one({"IEML" : ieml_proposition})