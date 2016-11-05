from unittest.case import TestCase

from handlers.intlekt.edition.visualisation import json_to_usl
from handlers import usl_to_json
from ieml.usl.tools import usl
from ieml.usl.tools import random_usl


class TestUSLsDecomposition(TestCase):
    def test_json_to_usl(self):
        _usl = random_usl()
        self.assertEqual(usl(json_to_usl({'json': usl_to_json({'usl': _usl})})), _usl)

    def test_usl_to_json(self):
        u = usl("[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([S:.-'B:.-'n.-S:.U:.-',])]*[([E:T:.f.-])])]")
        json = usl_to_json({'usl': u})
        self.assertEqual(json['type'], 'sentence-root-node')