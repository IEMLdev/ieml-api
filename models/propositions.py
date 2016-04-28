
from models.exceptions import PropositionAlreadyExists, ObjectTypeNotStoredinDB, ObjectNotFound
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

    def _write_proposition_to_db(self, proposition, proposition_tags, promotion=None):
        """Saves a proposition to the db"""
        entry = {
            "_id": str(proposition),
            "TYPE": self._proposition_db_type(proposition),
            "TAGS": {
                "FR": proposition_tags["FR"],
                "EN": proposition_tags["EN"]}}

        if promotion:
            entry["PROMOTION"] = {
                "TYPE": promotion["TYPE"],
                "IEML": promotion["IEML"]
            }

        self.propositions.insert_one(entry)

    def _check_proposition_exist(self, _id):
        return self.propositions.find_one({"_id": str(_id)}) is not None

    def save_closed_proposition(self, proposition_ast, proposition_tags):
        """Saves a valid proposition's AST into the database.
        A proposition being saved will always be a word, sentence or supersentence,
        As such, this function also saves the underlying primitives"""

        # for now, only does simple saving (whitout the Objectid matching stuff)
        # does check if the proposition is here or not beforehand though
        if self._check_proposition_exist(str(proposition_ast)):
            raise PropositionAlreadyExists()
        self._write_proposition_to_db(proposition_ast, proposition_tags)

    def save_promoted_proposition(self, new_proposition_ast, proposition_tags, old_proposition_ast):
        old_ieml = str(old_proposition_ast)
        promotion = {"IEML": old_ieml,
                     "TYPE": self._proposition_db_type(old_proposition_ast)}

        if self._check_proposition_exist(str(new_proposition_ast)):
            raise PropositionAlreadyExists()

        if not self._check_proposition_exist(old_ieml) and self._proposition_db_type(old_proposition_ast) != "TERM":
            raise ObjectNotFound()

        self._write_proposition_to_db(new_proposition_ast, proposition_tags, promotion)

    def search_for_propositions(self, search_string, max_level):
        if max_level == ieml.AST.Sentence:
            type_filter = {"$in": ["WORD", "SENTENCE"]}
        elif max_level == ieml.AST.SuperSentence:
            type_filter = {"$in": ["WORD", "SENTENCE", "SUPERSENTENCE"]}
        else:
            type_filter = "WORD"

        result = self.propositions.find({"$text": {"$search": search_string},
                                         "TYPE": type_filter},
                                        {"TAGS": 1, "TYPE": 1})

        return list(result)

    def exact_ieml_search(self, proposition):
        if isinstance(proposition, (ieml.AST.Sentence, ieml.AST.Word, ieml.AST.SuperSentence)):
            return self.propositions.find_one({"_id": str(proposition)})
        else:
            raise ObjectTypeNotStoredinDB()
        #
        # if proposition_db:
        #     return proposition_db
        # else:
        #     raise ObjectNotFound()
