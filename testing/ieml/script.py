import unittest

from ieml.operator import sc
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from ieml.script.script import MultiplicativeScript

scripts = list(map(sc, ["O:.E:M:.-"]))


class TestScript(unittest.TestCase):
    def test_script_class(self):
        self.assertEqual(sc('E:').script_class, AUXILIARY_CLASS)
        self.assertEqual(sc('O:').script_class, VERB_CLASS)
        self.assertEqual(sc('M:').script_class, NOUN_CLASS)

        self.assertEqual(sc('E:+O:').script_class, VERB_CLASS)
        self.assertEqual(sc('O:+M:').script_class, NOUN_CLASS)
        self.assertEqual(sc('I:').script_class, NOUN_CLASS)

    def test_multiplicative_layer0_nochildren(self):
        for s in scripts:
            layer0 = [m for m in s.tree_iter() if m.layer == 0 and isinstance(m, MultiplicativeScript)]
            for m in layer0:
                self.assertEqual(m.children, [], msg='Script %s have multiplicative node of layer 0 with children'%str(s))