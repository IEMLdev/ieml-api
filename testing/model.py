import models.base_queries
models.base_queries.DB_NAME = 'test_db'

from ieml.operator import *
from models.terms import TermsConnector
from models.relations import RelationsConnector
from models.base_queries import DBConnector
from models.constants import TERMS_COLLECTION, SCRIPTS_COLLECTION
from scripts import load_old_db
from testing.helper import *


class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # models.constants.DB_NAME = 'test_db'
        # connector = DBConnector()
        # connector.= self.client[DB_NAME]
        collections_name = DBConnector().db.collection_names(include_system_collections=False)

        if TERMS_COLLECTION not in collections_name or SCRIPTS_COLLECTION not in collections_name:
            load_old_db()

    def setUp(self):
        self.terms = TermsConnector()
        self.relations = RelationsConnector()

    def test_insert_term(self):
        script = sc("M:M:M:.U:U:U:.e.-")
        script.check()
        self.terms.add_term(script, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        self.assertTrue(self.terms.get_term(str(script))['_id'] == "M:M:M:.U:U:U:.e.-")
        self.terms.remove_term(script)
