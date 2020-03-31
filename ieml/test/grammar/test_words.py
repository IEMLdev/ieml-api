import unittest

from ieml.usl import Word, check_word
from ieml.usl.usl import usl


class WordsTest(unittest.TestCase):


    def test_old_words(self):
        WORDS = [
            "[! E:A:. (E:.wo.- E:S:.-d.u.-')(k.i.-l.i.-')]",
            "[E:T:. (E:.b.wa.- E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(e.) > E:.n.- (E:.wo.- E:S:.-d.u.-') > E:.d.- (E:.wo.- E:S:.-d.u.-')(m.-S:.U:.-') > ! E:.n.- E:U:. ()]",
            "[E:A:. (E:.wo.- E:.-n.S:.-' E:S:.-d.u.-')(b.a.- b.o.-n.o.-s.u.-' f.a.-b.a.-f.o.-') > E:A:. E:A:. (E:.wo.- E:S:.-d.u.-')(n.-S:.U:.-'B:.-'B:.-',B:.-',B:.-',_ n.-S:.U:.-'B:.-'B:.-',T:.-',S:.-',_) > ! E:A:. E:U:. ()]"
        ]

        for w in WORDS:
            u = usl(w)
            self.assertIsInstance(u, Word)
            self.assertNotEqual(w, str(u))
            self.assertIn('!', str(u))


    # def test_words_junctions(self):
    #     WORDS = [
    #         "[! E:A:. E:S:.-k.u.-' j.-U:.-'t.u.-t.u.-', (wa.) > E:A:. E:S:.-k.u.-' j.-A:.-'t.u.-t.u.-', ()]",
    #         "[E:B:. (E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(i.k.-) > ! E:.k.- (E:.wo.- E:.-n.S:.-' E:S:.-d.u.-')(b.a.-b.a.-f.o.-')]"
    #     ]
    #
    #     for w in WORDS:
    #         u = usl(w)
    #         self.assertIsInstance(u, Word)
    #         self.assertEqual(w, str(u))


    def test_singular_sequences(self):
        WORDS = [
            "[! E:A:. E:S:.-k.u.-' j.-U:.-'d.o.-l.o.-',  (m2(wa. we. wo. wu.)) > E:A:. E:S:.-k.u.-' j.-A:.-'d.o.-l.o.-', ()]",
            "[E:B:. (E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(m1(i.k.- A: T: S:)) > ! E:.k.- (E:.wo.- E:.-n.S:.-' E:S:.-d.u.-')(b.a.-b.a.-f.o.-')]",
            "[! E:S:. ()(u.A:.-) > E:.l.- (m1(E:.-U:.s.-l.-' E:.-U:.d.-l.-' E:.-A:.s.-l.-' E:.-A:.d.-l.-' E:.-B:.b.-l.-' E:.-B:.f.-l.-'))]"
        ]

        for w in WORDS:
            u = usl(w)
            self.assertGreater(u.cardinal, 1)
