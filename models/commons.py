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


def check_tags(tags, all_present=True):
    return isinstance(tags, dict) and (all(lang in tags for lang in TAG_LANGUAGES) or not all_present) \
           and all((tag in TAG_LANGUAGES and tag) for tag in tags) \
           and all(isinstance(tags[tag], str) for tag in tags)

def check_keywords(keywords):
    return isinstance(keywords, dict) and all((tag in TAG_LANGUAGES) for tag in keywords) \
           and all(isinstance(keywords[tag], list) for tag in keywords) \
           and all(isinstance(e, str) for tag in keywords for e in keywords[tag])
