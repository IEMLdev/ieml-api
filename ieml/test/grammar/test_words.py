import unittest

from ieml.usl import Word
from ieml.usl.usl import usl


class WordsTest(unittest.TestCase):
    def test_parse(self):
        word = "[E:.b.E:T:.- (E:T:.)(A:.e.-) > (E:.d.- E:.wo.- E:B:.-d.u.-' E:S:.j.-'j.-U:.-',) " \
               "(f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.n.-l.-'E:.-A:.n.-l.-',_) (E:.-B:.b.-l.-') > " \
               "! (E:.d.- E:A:. E:.wo.- E:S:.-d.u.-') (b.-S:.A:.-') > (E:.d.- E:A:. E:U:.) (m.u.-m.u.-d.u.-')]"
        u = usl(word)
        self.assertIsInstance(u, Word)
        self.assertEqual(str(u), word)