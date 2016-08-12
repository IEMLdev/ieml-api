from .db import BaseDBTest

from ieml import PropositionsParser
from ieml.object.tree_metadata import TreeElementMetadata


class TestMetadata(BaseDBTest):

    def setUp(self):
        super().setUp()
        TreeElementMetadata.set_connector(self.writable_db_connector)
        self.parser = PropositionsParser()
        self.example_word = self.parser.parse("[([a.wo.-]+[a.T:.-]+[i.t.-])*([wo.B:.-])]")
        self.writable_db_connector.save_closed_proposition(self.example_word, {"FR" : "WESH",
                                                                               "EN" : "SUP'"})

    def test_get_tags(self):
        self.assertEqual(self.example_word.metadata["TAGS"]["FR"], "WESH")
