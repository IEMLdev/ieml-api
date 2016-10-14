from unittest.case import TestCase

from ieml_objects.texts import Text
from ieml_objects.tools import RandomPoolIEMLObjectGenerator
from intlekt.edition.visualisation import usl_to_json


class TestUSLsDecomposition(TestCase):
    def test_usl_to_json(self):
        r = RandomPoolIEMLObjectGenerator(level=Text)
        print(usl_to_json({'usl': str(r.text())}))