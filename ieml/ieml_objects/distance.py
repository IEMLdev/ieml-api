import os

from ieml.ieml_objects.dictionary import Dictionary
from scipy.sparse.csgraph._shortest_path import shortest_path

from ieml.ieml_objects.tools import term

import numpy as np

# graph_nb_rel = Dictionary().relations_graph(['siblings', 'table_0'])
#
# graph_table = np.ones((len(Dictionary()),len(Dictionary()))) * 5
# for i in range(6):
#     for x, l in enumerate(Dictionary().relations[RELATIONS.index("table_%d"%i)]):
#         for y in l.indices:
#             graph_table[x, y] = 5 - i


def get_distance_m():
    FILE = '/tmp/dist_m.npy'
    if os.path.isfile(FILE):
        return np.load(FILE)
    else:
        graph_ethy = Dictionary().relations_graph(['etymology', 'inclusion', 'siblings']).astype(np.float32)
        # for x, y in zip(*np.where(graph_ethy != 0)):
        #     graph_ethy[x, y] = 1/graph_ethy[x, y]
        # graph_ethy.tocsr()

        dist_m = shortest_path(graph_ethy, directed=True, unweighted=False)
        np.save(FILE, dist_m)
        return dist_m


# dist_m_nb_rel = shortest_path(graph_nb_rel, directed=True, unweighted=True)
#
# dist_table = shortest_path(graph_table, directed=True, unweighted=False)


distance_m = get_distance_m()
def _distance_etymology(term0, term1):
    return distance_m[term0.index, term1.index]

def _nb_relations(term0, term1):
    # print(term0.relations.to(term1, table=False))
    return 5 - len(term0.relations.to(term1, ['opposed', 'associated', 'crossed', 'twin', 'table_0']))

def _max_rank(term0, term1):
    rel_table = term0.relations.to(term1, ['table_%d'%i for i in range(1, 6)])
    # print(rel_table)
    if 'table_5' in rel_table:
        return 0

    if 'table_4' in rel_table:
        return 1

    if 'table_3' in rel_table:
        return 2

    if 'table_2' in rel_table:
        return 3

    if 'table_1' in rel_table:
        return 4

    return 5


def distance(term0, term1):
    if term0 == term1:
        return 0,0,0

    if term0.script.paradigm or term1.script.paradigm:
        raise ValueError("Not implemented for paradigms")

    return _distance_etymology(term0, term1), _nb_relations(term0, term1), _max_rank(term0, term1)

    # print(term0.relations.to(term1))
    # print(term1.relations.to(term0))



def test_term(t):
    print("Distance from term %s -- %s"%(str(t), t.translation['fr']))

    for d, tt in sorted((distance(t, t1) ,t1) for t1 in Dictionary() if not t1.script.paradigm)[:30]:
        print("%s (%d, %d, %d) - %s"%(str(tt), d[0], d[1], d[2], tt.translation['fr']))


if __name__ == '__main__':

    test_term(term("y."))


    # print(distance(term("E:U:.k.-"), term("E:U:.m.-")))
    # print(distance(term("y."), term("j.")))
    # print(distance(term("y."), term("g.")))
    #
    # root = term("M:M:.o.-M:M:.o.-E:.-+s.u.-'")
    # ss = [term(s) for s in root.script.singular_sequences]
    #
    # print(ss[34].translation['fr'])
    # print([t.translation['fr'] for t in sorted(ss, key=lambda t1: distance(ss[34], t1))])
