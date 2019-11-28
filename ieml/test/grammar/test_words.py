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


    def test_old_words(self):
        WORDS = [
            # "[E:.b.E:B:.- ! E:A:. (E:.wo.- E:S:.-d.u.-')(k.i.-l.i.-')]",
            # "[E:.b.E:T:.- E:T:. (E:.b.wa.- E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(e.) > E:.n.- (E:.wo.- E:S:.-d.u.-') > E:.d.- (E:.wo.- E:S:.-d.u.-')(m.-S:.U:.-') > ! E:.n.- E:U:. ()]",
            "[E:.b.E:T:.- E:A:. (E:.wo.- E:.-n.S:.-' E:S:.-d.u.-')(b.a.- b.o.-n.o.-s.u.-' f.a.-b.a.-f.o.-') > E:A:. E:A:. (E:.wo.- E:S:.-d.u.-')(n.-S:.U:.-'B:.-'B:.-',B:.-',B:.-',_ n.-S:.U:.-'B:.-'B:.-',T:.-',S:.-',_) > ! E:A:. E:U:. ()]"
        ]

        for w in WORDS:
            u = usl(w)
            self.assertIsInstance(u, Word)
            self.assertNotEqual(w, str(u))
            self.assertIn('!', str(u))


    def test_words_junctions(self):
        WORDS = [
            # "[! E:A:. E:S:.-k.u.-' j.-U:.-'t.u.-t.u.-', (wa.) >"
            # " E:A:. E:S:.-k.u.-' j.-A:.-'t.u.-t.u.-', ()]",
            "[E:B:. (E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(i.k.-) > ! E:.k.- (E:.wo.- E:.-n.S:.-' E:S:.-d.u.-')(b.a.-b.a.-f.o.-')]"
        ]

        for w in WORDS:
            u = usl(w)
            self.assertIsInstance(u, Word)
            self.assertEqual(w, str(u))


