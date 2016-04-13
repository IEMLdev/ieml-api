from handlers import WordGraphValidatorHandler
from .helpers import *

class TestGraphValidator(unittest.TestCase):

    def setUp(self):
        self.word_handler = WordGraphValidatorHandler()
        self.word_handler.json_data = {"nodes" : [{"id" : 1,
                                                   "ieml_string" : "[a.i.-]"},
                                                  {"id" : 2,
                                                   "ieml_string" : "[i.i.-]"},
                                                  {"id" : 3,
                                                   "ieml_string" : "[E:A:T:.]"},
                                                  {"id" : 4,
                                                   "ieml_string" : "[E:S:.wa.-]"},
                                                  {"id" : 5,
                                                   "ieml_string" : "[E:S:.o.-]"}
                                                  ],
                                       "graph": {"substance" : [1,2],
                                                 "mode" : [3,4,5]
                                                 },
                                       "tag" : "Faire du bruit avec sa bouche"
                                       }
        self.word_handler.db_connector = Mock()

    def test_word_validation(self):
        """Tests the whole word validation code block without the request handling"""

        request_output = self.word_handler.post()
        word = get_test_word_instance()
        word.check()
        self.assertEquals(request_output["ieml"], str(word))
