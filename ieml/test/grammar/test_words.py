import unittest

from ieml.usl import Word, check_word
from ieml.usl.usl import usl


class WordsTest(unittest.TestCase):
    def test_parse(self):
        word = "[E:.b.E:T:.- (E:U:. E:A:. E:.d.-)(m.u.-m.u.-d.u.-') > !(E:A:. E:.wo.- E:.d.- E:S:.-d.u.-')(b.-S:.A:.-')" \
               " > (E:T:. E:.-wo.-t.o.-' E:.-'wo.-S:.-'t.o.-',)(A:.e.-) > (E:.wo.- E:.d.- E:B:.-d.u.-')" \
               "(f.o.-f.o.-'E:.-U:.t.-l.-',E:.-U:.n.-l.-'E:.-A:.n.-l.-',_)(E:.-B:.b.-l.-' E:S:.j.-'j.-U:.-',)]"
        u = usl(word)
        check_word(u)
        self.assertIsInstance(u, Word)
        self.assertEqual(word, str(u))

