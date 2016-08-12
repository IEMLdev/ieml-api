import re

from pymongo.errors import DuplicateKeyError

import ieml.AST
import ieml.object.terms
from models.exceptions import PropositionAlreadyExists, ObjectTypeNotStoredinDB, ObjectNotFound
from .base_queries import DBConnector
from .constants import PROPOSITION_COLLECTION, TAG_LANGUAGES


class PropositionsQueries(DBConnector):
    def __init__(self):
        super().__init__()
        self.propositions = self.db[PROPOSITION_COLLECTION]

    @staticmethod
    def _proposition_db_type(proposition):
        """Returns the DB name for a proposition"""
        return proposition.__class__.__name__.upper()

    def check_tags_available(self, tags):
        for language in tags:
            if self.check_tag_exist(tags[language], language):
                return False
        return True

    def check_tag_exist(self, tag, language):
        return self.propositions.find_one({'TAGS.' + language: tag}) is not None

    def check_proposition_stored(self, proposition):
        """Retrieves the objectid of an IEML primitive"""
        if isinstance(proposition, ieml.object.terms.Term):
            return self.old_terms.find_one({"IEML": proposition.ieml}) is not None
        elif isinstance(proposition, (ieml.AST.Sentence, ieml.AST.Word, ieml.AST.SuperSentence)):
            return self._check_proposition_exist(str(proposition))
        else:
            raise ObjectTypeNotStoredinDB()

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

        try:
            self.propositions.insert_one(entry)
        except DuplicateKeyError:
            raise PropositionAlreadyExists()

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

    def _format_response(self, response):
        return {
            "IEML": response['_id'],
            "TAGS": response['TAGS'],
            "TYPE": response['TYPE']
        }

    def search_propositions(self, search_string, languages=None, levels=None):
        query = {}

        if levels:
            query['TYPE'] = {"$in": [level.__name__.upper() for level in levels]}

        regex = {'$regex': re.compile(re.escape(search_string))}
        conditions = [{'_id': regex}]

        if languages:
            for language in languages:
                conditions.append({'TAGS.' + language: regex})
        else:
            for language in TAG_LANGUAGES:
                conditions.append({'TAGS.' + language: regex})

        query['$or'] = conditions

        result = self.propositions.find(query)

        return [self._format_response(entry) for entry in result]

    def exact_ieml_search(self, proposition):
        if isinstance(proposition, (ieml.AST.Sentence, ieml.AST.Word, ieml.AST.SuperSentence)):
            entry = self.propositions.find_one({"_id": str(proposition)})
            if entry:
                return self._format_response(entry)
            else:
                raise ObjectNotFound()
        else:
            raise ObjectTypeNotStoredinDB()

    def update_tags(self, ieml, tags_dict):
        """Updates the tag of a proposition identified by the input IEML"""
        self.propositions.update_one({'_id': ieml},
                                     {'$set': {'TAGS': tags_dict}})
