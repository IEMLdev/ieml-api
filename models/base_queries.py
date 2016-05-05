from random import randint
import re
from pymongo import MongoClient

from models.constants import TERMS_COLLECTION, TAG_LANGUAGES
from .constants import DB_ADDRESS, DB_NAME


class DBConnector(object):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS) # connecting to the db
        self.db = self.client[DB_NAME] # opening a DB
        self.terms = self.db[TERMS_COLLECTION]


class DictionaryQueries(DBConnector):
    """Class mainly used for anything related to the terms collection, i.e., the dictionnary"""

    def search_for_terms(self, search_string):
        """Searching for terms containing the search_string, both in the IEML field and translated field"""
        regex = re.compile(search_string)

        result = [{"term_id" : str(term["_id"]),
                   "ieml" : term["IEML"],
                   "natural_language" : {"FR" : term.get("FR"),
                                         "EN" : term.get("EN")},
                   "paradigm": False if term["PARADIGM"] == "0" else True}
                  for term in self.terms.find(
                    {'$or': [
                        {'IEML': {'$regex': regex}},
                        {'FR': {'$regex': regex}},
                        {'EN': {'$regex': regex}}]},
                    {"IEML" : 1, "FR" : 1, "EN" : 1, "PARADIGM" : 1})]
        return result

    def exact_ieml_term_search(self, ieml_string):
        return self.terms.find_one({"IEML": ieml_string})

    def get_random_terms(self, count):
        """Used by the random proposition generator : ouputs n random terms from the dicitonary DB, n being count"""
        total_count = self.terms.count()
        return [term["IEML"] for term in self.terms.find().limit(count).skip(randint(0, total_count - 1))]


class Tag:
    @staticmethod
    def check_tags(tags):
        return all(lang in tags for lang in TAG_LANGUAGES)
