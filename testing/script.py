import unittest

from ieml.operator import sc
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS


class TestScript(unittest.TestCase):
    def test_script_class(self):
        self.assertEqual(sc('E:').script_class, AUXILIARY_CLASS)
        self.assertEqual(sc('O:').script_class, VERB_CLASS)
        self.assertEqual(sc('M:').script_class, NOUN_CLASS)

        self.assertEqual(sc('E:+O:').script_class, VERB_CLASS)
        self.assertEqual(sc('O:+M:').script_class, NOUN_CLASS)
        self.assertEqual(sc('I:').script_class, NOUN_CLASS)