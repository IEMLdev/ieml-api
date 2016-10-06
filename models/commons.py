from pymongo import MongoClient

from helpers.metaclasses import Singleton
from models.constants import TAG_LANGUAGES
from .constants import OLD_TERMS_COLLECTION
from config import DB_ADDRESS, DB_NAME, OLD_DB_NAME


class DBConnector(object, metaclass=Singleton):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS)  # connecting to the db

        self.db = self.client[DB_NAME] # opening a DB
        self.old_db = self.client[OLD_DB_NAME]

        # TODO : once the old DB has a migration parser, this should be in the self.db
        self.old_terms = self.old_db[OLD_TERMS_COLLECTION]


def check_tags(tags):
    return isinstance(tags, dict) and all(lang in tags for lang in TAG_LANGUAGES) \
           and all((tag in TAG_LANGUAGES and tag) for tag in tags) \
           and all(isinstance(tags[tag], str) for tag in tags)
