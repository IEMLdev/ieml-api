from progressbar import ProgressBar

from ieml.script.tools import factorize
import unittest

from models.terms.terms import TermsConnector
from ieml.operator import sc

class FactorizationTest(unittest.TestCase):
    def setUp(self):
        self.terms = TermsConnector()

    def test_all_terms(self):
        exept = {"M:M:.-O:M:.-E:.-+s.y.-'+M:M:.-M:O:.-E:.-+s.y.-'",
                 *{"%s.-O:M:.-+M:O:.-s.y.-'"%s for s in 'sbtkmnfl'},
                 "M:M:.-O:M:.-'+M:M:.-M:O:.-'",
                 "M:M:.-O:M:.-s.y.-'+M:M:.-M:O:.-s.y.-'"}
        term = self.terms.get_all_terms()
        for t in term:
            if t['_id'] in exept:
                continue
            self.assertEqual(t['_id'], str(factorize(sc(t['_id']))))

