from pymongo import MongoClient

from models.constants import TERMS_COLLECTION
from .constants import DB_ADDRESS, DB_NAME

class DBConnector(object):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS) # connecting to the db
        self.db = self.client[DB_NAME] # opening a DB
        self.terms = self.db[TERMS_COLLECTION]


class DictionnaryQueries(DBConnector):
    """Class mainly used for anything related to the terms collection, i.e., the dictionnary"""

    def search_for_terms(self, search_string):
        """Searching for terms containing the search_string, both in the IEML field and translated field"""

        result = [{"term_id" : str(term["_id"]),
                   "ieml" : term["IEML"],
                   "natural_language" : {"FR" : term.get("FR"),
                                         "EN" : term.get("EN")}}
                  for term in self.terms.find({"$text" : {"$search" : search_string}},
                                              {"IEML" : 1, "FR" : 1, "EN" : 1})]
        return result

    def search_for_ieml_terms(self, ieml_string):
        """Does the search with an IEML string, and not the translated field"""
        return list(self.terms.find({"$text" : {"$search" : ieml_string}},
                                    {"IEML" : 1}))