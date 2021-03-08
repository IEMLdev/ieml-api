import unittest

from ieml.test.grammar.examples import WORDS_EXAMPLES
from ieml.usl import Word
from ieml.usl.syntagmatic_function import SyntagmaticFunction
from ieml.usl.usl import usl


class SyntagmaticFunctionTest(unittest.TestCase):

    def test_to_list_bijection(self):
        for w_S in WORDS_EXAMPLES:
            w = usl(w_S)
            self.assertIsInstance(w, Word)
            sfun = w.syntagmatic_fun
            sfun_l = sfun.as_list(w.context_type)

            ctx_t, sfun_2 = SyntagmaticFunction.from_list(sfun_l)
            self.assertEqual(sfun, sfun_2)

