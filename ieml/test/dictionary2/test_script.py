import unittest

from ieml.exceptions import TooManySingularSequences
from ieml.dictionary2.script import script as sc, m
from ieml.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS, PRIMITIVES
from ieml.dictionary2.script import MultiplicativeScript, AdditiveScript

scripts = list(map(sc, ["O:.E:M:.-"]))


class TestScript(unittest.TestCase):
    def test_script_class(self):
        self.assertEqual(sc('E:').script_class, AUXILIARY_CLASS)
        self.assertEqual(sc('O:').script_class, VERB_CLASS)
        self.assertEqual(sc('M:').script_class, NOUN_CLASS)

        self.assertEqual(sc('E:+O:').script_class, VERB_CLASS)
        self.assertEqual(sc('O:+M:').script_class, NOUN_CLASS)
        self.assertEqual(sc('I:').script_class, NOUN_CLASS)

    def test_multiplication(self):
        sub = sc('wa.')
        att = sc('u.')
        mode = sc('O:.')

        r = m(substance=sub, attribute=att, mode=mode)
        self.assertEqual(r.layer, 2)
        self.assertIsInstance(r, MultiplicativeScript)
        self.assertListEqual(r.children, [sub, att, mode])

    def test_multiplicative_layer0_nochildren(self):
        for s in scripts:
            layer0 = [m for m in s.tree_iter() if m.layer == 0 and isinstance(m, MultiplicativeScript)]
            for m in layer0:
                self.assertEqual(m.children, [], msg='Script %s have multiplicative node of layer 0 with children'%str(s))

    def test_order_primitive(self):
        primitives = [sc(p + ':') for p in PRIMITIVES]
        primitives.sort()
        res = ''.join([str(p)[0:1] for p in primitives])
        self.assertEqual(res, 'EUASBT', msg='Primitives not correctly sorted.')

    def test_too_many_singular_sequences(self):
        with self.assertRaises(TooManySingularSequences):
            sc('F:F:F:.F:F:F:.-')

    def test_str(self):
        self.assertIsNotNone(MultiplicativeScript(character='A')._str)
        self.assertIsNotNone(AdditiveScript(character='O')._str)