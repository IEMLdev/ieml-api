from ieml.usl.tools import random_usl, RandomUslGenerator
from ieml.usl.usl import Usl
from ieml.syntax import Text, Word, Sentence
import numpy as np



def square_order_matrix(usl_list):
    usl_list = list(usl_list)
    indexes = {
        u: i for i, u in enumerate(usl_list)
    }

    order_mat = np.zeros(shape=(len(usl_list), len(usl_list)), dtype=int)

    for u in usl_list:
        sorted_list = QuerySort(u).sort(collection=usl_list)
        for i, u_s in enumerate(sorted_list):
            order_mat[indexes[u], indexes[u_s]] = i

    return order_mat

class QuerySort:
    def __init__(self, usl):
        self.usl = usl

        assert isinstance(usl, Usl)

    def sort(self, collection):

        def sort_key(u):
            return self._proximity(u, lambda u: u.glossary)
            # self._proximity(u, lambda u: u.topics)

        return sorted(collection, key=sort_key)


    def _proximity(self, u, get_set):
        s0 = get_set(self.usl)
        s1 = get_set(u)
        sym_diff = len(s0 ^ s1)

        if sym_diff != 0:
            return len(s0.intersection(s1)) / sym_diff
        else:
            # same subject
            # use max of ( len(g0.intersection(g1)) / sym_diff ) + 1
            return len(s0) + 1


if __name__ == '__main__':

    gen = RandomUslGenerator(pool_size=100, level=Text)

    usls = [gen(Sentence) for _ in range(10)]
    for i, u in enumerate(usls):
        print("{0} - {1}".format(i,len(u.glossary)))
    print(square_order_matrix(usls))
