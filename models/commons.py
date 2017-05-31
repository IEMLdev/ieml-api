from itertools import islice

from pymongo import MongoClient

from config import DB_ADDRESS, DB_NAME
from ieml.commons import LANGUAGES
from metaclasses import Singleton
from models.constants import TAG_LANGUAGES


class DBConnector(object, metaclass=Singleton):
    """Automatically connects when instantiated"""

    def __init__(self):
        self.client = MongoClient(DB_ADDRESS)  # connecting to the db

        self.db = self.client[DB_NAME] # opening a DB


def create_translations_indexes(collection):
    for language in TAG_LANGUAGES:
        collection.create_index('TRANSLATIONS.%s'%language, unique=True,
                                partialFilterExpression={'TRANSLATIONS.%s'%language: { '$exists': True }})

def check_tags(tags, all_present=True):
    return isinstance(tags, dict) and (all(lang in tags for lang in TAG_LANGUAGES) or not all_present) \
           and all((tag in TAG_LANGUAGES and tag) for tag in tags) \
           and all(isinstance(tags[tag], str) for tag in tags)


def check_keywords(keywords):
    return isinstance(keywords, dict) and all((tag in TAG_LANGUAGES) for tag in keywords) \
           and all(isinstance(keywords[tag], list) for tag in keywords) \
           and all(isinstance(e, str) for tag in keywords for e in keywords[tag])


def generate_translations(usl):
    result = {}
    entries = sorted([t for p, t in usl.paths.items()])
    for l in LANGUAGES:
        result[l.upper()] = ' '.join((e.translation[l] for e in islice(entries, 10)))

    return result

generate_tags = generate_translations