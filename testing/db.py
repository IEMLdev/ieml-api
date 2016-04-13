from .helpers import *
from models import PropositionsQueries

class TestDBQueries(unittest.TestCase):

    def setUp(self):
        self.writable_db_connector = PropositionsQueries()
        # we replace the actual collection by a "fake" one:
        self.writable_db_connector.propositions = self.writable_db_connector.db["prop_test"]

    def tearDown(self):
        self.writable_db_connector.propositions.drop() #cleaning up!

    def test_write_word_to_db(self):
        word_object = get_test_word_instance()
        word_object.check()
        self.writable_db_connector.save_closed_proposition(word_object, "Faire du bruit avec sa bouche")
        self.assertEquals(self.writable_db_connector.propositions.count(), 1)
