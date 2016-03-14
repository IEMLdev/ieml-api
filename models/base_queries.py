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

    def search_for_terms(self, search_string):
        """Searching for terms containing the search_string, both in the IEML field and translated field"""

        result = [{"term_id" : str(term["_id"]),
                   "ieml" : term["IEML"],
                   "natural_language" : {"FR" : term["FR"],
                                         "EN" : term["EN"]}}
                  for term in self.terms.find({"$text" : {"$search" : search_string}},
                                              {"IEML" : 1, "FR" : 1, "EN" : 1})]
        return result