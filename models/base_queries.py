from pymongo import MongoClient
from .constants import DB_ADDRESS, DB_NAME

class DBConnector(object):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS) # connecting to the db
        self.db = self.client[DB_NAME] # opening a DB


    def pipeline_example(self, round_number):
        """Mongodb pipeline example"""

        example_pipeline = [
            {"$group" : { "_id" : 1,
                          "total_inscrit" : {"$sum" : "$registered_voters"}}}
        ]
        result = next(self.db(round_number).aggregate(example_pipeline))
        return result