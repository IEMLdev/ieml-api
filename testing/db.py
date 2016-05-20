from .helper import *
import string, random
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from models import *
from ieml.AST import Sentence, Word


class BaseDBTest(unittest.TestCase):

    def setUp(self):
        self.writable_db_connector = PropositionsQueries()
        # we replace the actual collection by a "fake" one:
        self.writable_db_connector.propositions = self.writable_db_connector.db["prop_test"]
        self.term_connector = DictionaryQueries()

    def tearDown(self):
        self.writable_db_connector.propositions.drop()  # cleaning up!


class TestDBQueries(BaseDBTest):

    def test_write_word_to_db(self):
        word_object = get_test_word_instance()
        word_object.check()
        self.writable_db_connector.save_closed_proposition(word_object, {"FR" : "Faire du bruit avec sa bouche",
                                                                         "EN" : "Badababi dou baba boup"})
        self.assertEqual(self.writable_db_connector.propositions.count(), 1)

    def test_search(self):
        result = self.term_connector.search_for_terms("w")
        self.assertTrue(len(result) != 0)

        result = self.term_connector.search_for_terms("possessif")
        self.assertTrue(len(result) != 0)
        for e in result:
            self.assertIn("possessif", e['TAGS']['FR'])


class TestUnicityDb(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient(DB_ADDRESS)  # connecting to the db
        self.db = self.client[DB_NAME]  # opening a DB
        self.collections = [self.db[PROPOSITION_COLLECTION], self.db[TEXT_COLLECTION], self.db[HYPERTEXT_COLLECTION]]

        self.tags = {'EN' : "test unicity unit test", 'FR' : "test de l'unicité unit test"}

    def _save_to_db(self):
        count = 0
        for collection in self.collections:
            try:
                collection.insert_one({
                    "_id": ''.join(random.sample(string.ascii_letters, 20)),
                    "TYPE": "test_unicity",
                    "TAGS": {
                        "FR": "test_unicity",
                        "EN": "test_unicity"
                    }})
            except DuplicateKeyError:
                count += 1

        return count == 3

    def tearDown(self):
        for collection in self.collections:
            collection.delete_many({"TAGS.FR": "test_unicity"})

    def test_unicity_on_tags(self):
        self._save_to_db()
        self.assertEqual(self._save_to_db(), True)

