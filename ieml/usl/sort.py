from ieml.usl.usl import Usl
import numpy as np

class QuerySort:
    def __init__(self, usl):
        self.usl = usl

        assert isinstance(usl, Usl)

    def __call__(self, *args, **kwargs):
        return sorted(args[0], key=self._word_proximity)

    def _word_proximity(self, u):
        # an ensemblist word ordering
        g0 = self.usl.glossary
        g1 = u.glossary

        sym_diff = len(g0.symetric_difference(g1))

        if sym_diff != 0:
            return len(g0.intersection(g1)) / sym_diff
        else:
            # same subject
            # use max of ( len(g0.intersection(g1)) / sym_diff ) + 1
            return len(g0) + 1

    # def _relations_product(self, u):
    #     for t in u.glossary:
    #         t

