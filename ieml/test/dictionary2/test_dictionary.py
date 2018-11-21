import unittest

from ieml.dictionary2.dictionary import Dictionary
import numpy as np

from ieml.dictionary2.script import Script


class DictionaryTestCase(unittest.TestCase):

    def setUp(self):
        self.d = Dictionary.load('/home/louis/code/ieml/ieml-dictionary/dictionary')

    def test_scripts(self):
        self.assertIsInstance(self.d.scripts, np.ndarray)
        self.assertEqual(self.d.scripts.ndim, 1)
        self.assertEqual(self.d.scripts.shape, (len(self.d),))
        for s in self.d.scripts:
            self.assertIsInstance(s, Script)

    def test_one_hot(self):
        for i, s in enumerate(self.d.scripts):
            oh = self.d.one_hot(s)

            self.assertIsInstance(oh, np.ndarray)
            self.assertEqual(oh.ndim, 1)
            self.assertEqual(oh.shape, (len(self.d),))
            self.assertEqual(oh.dtype, int)

            self.assertTrue(all(e == 0 for j, e in enumerate(oh) if j != i))
            print(oh[i-2:i+2], s)

            self.assertEqual(oh[i], 1)
