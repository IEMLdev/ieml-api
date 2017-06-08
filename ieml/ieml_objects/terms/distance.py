import os
from collections import defaultdict

from ieml.ieml_objects.terms.dictionary import Dictionary
from scipy.sparse.csgraph._shortest_path import shortest_path

from ieml.ieml_objects.terms.tools import term

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
    FILE_w = '/tmp/dist_m_w.npy'

    if os.path.isfile(FILE) and os.path.isfile(FILE_w):
        return np.load(FILE), np.load(FILE_w)
    else:
        graph_ethy = Dictionary().relations_graph({
            'etymology': 1.0, # 1 to 0 (1/(layer0 - layer1)**2
            'inclusion': 1.0, # 0 or 1
            'siblings' : 1.5, # 0 or 1
            'table'    : 1/3 # 0 to 6
        })
        # graph_ethy_m = Dictionary().relations_graph(['etymology', 'inclusion', 'siblings',
        #                                            'table_0', 'table_1', 'table_2', 'table_3',
        #                                            'table_4', 'table_5']).astype(np.float32).todense()

        graph_ethy = 1.0/graph_ethy
        graph_ethy[graph_ethy == np.inf] = 0

        # for x, y in zip(*np.where(graph_ethy != 0)):
        #     graph_ethy[x, y] = 1/graph_ethy[x, y]
        # graph_ethy.tocsr()
        # dist_m = shortest_path(graph_ethy, directed=False, unweighted=True)
        dist_m_w, pred = shortest_path(graph_ethy, directed=False, unweighted=False, return_predecessors=True)
        np.save(FILE, pred)
        np.save(FILE_w, dist_m_w)
        # dist_m = None
        return pred, dist_m_w


# dist_m_nb_rel = shortest_path(graph_nb_rel, directed=True, unweighted=True)
#
# dist_table = shortest_path(graph_table, directed=True, unweighted=False)


pred, distance_m_w = get_distance_m()
def _distance_etymology(term0, term1):
    i = 0.0
    index = term1.index
    while index != term0.index:
        i += 1.0
        index = pred[term0.index, index]
        if index == -9999:
            return 9999

    return i

def _nb_relations(term0, term1):
    # print(term0.relations.to(term1, table=False))
    return distance_m_w[term0.index, term1.index]
    # 5 - len(term0.relations.to(term1, ['opposed', 'associated', 'crossed', 'twin', 'table_0']))

def _max_rank(term0, term1):
    rel_table = term0.relations.to(term1, ['table_%d'%i for i in range(1, 6)])
    # print(rel_table)
    if 'table_5' in rel_table:
        return 0

    if 'table_4' in rel_table:
        return 0

    if 'table_3' in rel_table:
        return 1

    if 'table_2' in rel_table:
        return 2

    if 'table_1' in rel_table:
        return 3

    return 4
    # return 4 + abs(term0.script.layer - term1.script.layer)



def distance(term0, term1):
    if term0 == term1:
        return 0.,0.,0.

    # if term0.script.paradigm or term1.script.paradigm:
    #     raise ValueError("Not implemented for paradigms")

    return _distance_etymology(term0, term1), _nb_relations(term0, term1), _max_rank(term0, term1)

    # print(term0.relations.to(term1))
    # print(term1.relations.to(term0))


def ranking_from_term(term0, nb_terms=30):
    other = sorted((_distance_etymology(term0, t1), _nb_relations(term0, t1) ,t1) for t1 in Dictionary() if not t1.script.paradigm)

    return other[:nb_terms]


def _test_diagram(t):
    print("Diagram for term %s -- %s"%(str(t), t.translations.fr))

    other = sorted((distance(t, t1) ,t1) for t1 in Dictionary() if t1 != t)

    cat = defaultdict(list)
    for d, tt in other:
        for rel in t.relations.to(tt, relations_types=['father', 'child', 'contains', 'contained', 'table', 'siblings']):
            cat[rel].append((d, tt))

    for rel in cat:
        cat[rel] = [(d,tt) for d, tt in sorted(cat[rel]) if d[1] <= 1.0]

    for k, v in cat.items():
        print("\t[%s]"%k)
        for d, tt in v:
            print("%s (%.2f, %.2f, %.2f) - %s [%s]" % (str(tt), d[0], d[1], d[2], tt.translations.fr,
                                                       ', '.join(t.relations.to(tt))))


def _test_term(t):
    print("Distance from term %s -- %s"%(str(t), t.translation['fr']))
    other = sorted((distance(t, t1) ,t1) for t1 in Dictionary() if not t1.script.paradigm)
    kkk = [t for t in other if t[0][1] < 2.0]
    for d, tt in kkk[:30]:
        print("%s (%.2f, %.2f, %.2f) - %s [%s]"%(str(tt), d[0], d[1], d[2], tt.translation['fr'],
                                                 ', '.join(t.relations.to(tt))))


if __name__ == '__main__':

    # _test_term(term("wa."))
    _test_diagram(term("l.-y.-s.y.-'"))
    # print(term("j.-'U:.-'k.o.-t.o.-',").relations.to(term("[j.-'B:.-'k.o.-t.o.-',]")))
    # print(distance(term("j.-'U:.-'k.o.-t.o.-',"), term("k.o.-t.o.-'")))

    graph_ethy = Dictionary().relations_graph({
        'etymology': 2.0,
        'inclusion': 1.0,
        'siblings': 1.5,
        'table': 1/3
    })

    # print(distance(term("E:U:.k.-"), term("E:U:.m.-")))
    # print(distance(term("y."), term("j.")))
    # print(distance(term("y."), term("g.")))
    #
    # root = term("M:M:.o.-M:M:.o.-E:.-+s.u.-'")
    # ss = [term(s) for s in root.script.singular_sequences]
    #
    # print(ss[34].translation['fr'])
    # print([t.translation['fr'] for t in sorted(ss, key=lambda t1: distance(ss[34], t1))])
