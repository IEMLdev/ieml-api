from pymongo import MongoClient
from .constants import DB_ADDRESS

class DBConnector(object):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS) # connecting to the db
        self.db = self.client['polldata'] # opening a DB


    def pipeline_example(self, round_number):
        """Données pour toute la france"""

        example_pipeline = [
            {"$group" : { "_id" : 1,
                          "total_inscrit" : {"$sum" : "$registered_voters"}}}
        ]
        result = next(self.db(round_number).aggregate(example_pipeline))
        return result