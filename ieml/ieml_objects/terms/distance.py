import os
from itertools import product, groupby

from ieml.ieml_objects.terms import Dictionary, Table
from collections import defaultdict

from scipy.sparse.csgraph._shortest_path import shortest_path

from ieml.ieml_objects.terms.tools import term, TermNotFoundInDictionary

import numpy as np

from ieml.ieml_objects.terms.version import get_default_dictionary_version
from ieml.script.constants import MAX_LAYER
from ieml.script.script import MultiplicativeScript, NullScript, AdditiveScript

__distance_mat = {}


def get_distance_matrix(version):
    if version not in __distance_mat:
        __distance_mat[version] = load_distance_matrix(version)

    return __distance_mat[version]


def load_distance_matrix(version):
    FILE = '/tmp/distance_m_%s.npy'%str(version)
    FILE_w = '/tmp/distance_m_w_%s.npy'%str(version)

    if os.path.isfile(FILE) and os.path.isfile(FILE_w):
        return np.load(FILE), np.load(FILE_w)
    else:
        graph_ethy = Dictionary(version).relations_graph({
            'etymology': 1.0, # 1 to 0 (1/(layer0 - layer1)**2
            'inclusion': 1.0, # 0 or 1
            'siblings' : 1.5, # 0 or 1
            'table'    : 1/3  # 0 to 6
        })
        # graph_ethy_m = Dictionary().relations_graph(['etymology', 'inclusion', 'siblings',
        #                                            'table_0', 'table_1', 'table_2', 'table_3',
        #                                            'table_4', 'table_5']).astype(np.float32).todense()

        graph_ethy = 1.0/graph_ethy

        graph_ethy[graph_ethy == np.inf] = 0

        # dist_m = shortest_path(graph_ethy, directed=False, unweighted=True)
        dist_m_w, pred = shortest_path(graph_ethy, directed=False, unweighted=False, return_predecessors=True)
        np.save(FILE, pred)
        np.save(FILE_w, dist_m_w)
        # dist_m = None
        return pred, dist_m_w


def _distance_etymology(term0, term1):
    i = 0.0
    index = term1.index
    pred = get_distance_matrix(term0.dictionary.version)[0]
    while index != term0.index:
        i += 1.0
        index = pred[term0.index, index]
        if index == -9999:
            return 9999

    return i


def _nb_relations(term0, term1):
    return get_distance_matrix(term0.dictionary.version)[1][term0.index, term1.index]


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

    return _distance_etymology(term0, term1), _nb_relations(term0, term1), _max_rank(term0, term1)



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


def _test_term(t, distance_f=distance):
    print("Distance from term %s -- %s"%(str(t), t.translations['fr']))

    other = sorted((distance_f(t, t1) ,t1) for t1 in Dictionary() if not t1.script.paradigm)
    kkk = [t for t in other if t[0][1] < 2.0]
    for d, tt in kkk[:30]:
        print("%s (%.2f, %.2f, %.2f) - %s [%s]"%(str(tt), d[0], d[1], d[2], tt.translations['fr'],
                                                 ', '.join(t.relations.to(tt))))

__graph_ethy = None
def distance2(t0, t1):
    global __graph_ethy
    if __graph_ethy is None:
        __graph_ethy = Dictionary().relations_graph({
            'etymology': 1.0, # 1 to 0 (1/(layer0 - layer1)**2
            'inclusion': 1.0, # 0 or 1
            'siblings' : 1.5, # 0 or 1
            'table'    : 1/3  # 0 to 6
        })
        __graph_ethy = np.exp(-__graph_ethy)
        for i in range(__graph_ethy.shape[0]):
            __graph_ethy[i, i] = 0

    v = __graph_ethy[t0.index, t1.index] - __graph_ethy[t1.index, :]
    return __graph_ethy[t0.index, t1.index]#np.sum(np.dot(v, v.transpose()))


def _test_term2(t):
    print("Distance from term %s -- %s, with tanh distance"%(str(t), t.translations['fr']))

    other = sorted((distance2(t, t1), t1) for t1 in Dictionary() if not t1.script.paradigm)
    kkk = [t for t in other if t[0] < 1.0]
    for d, tt in kkk[:30]:
        print("%s (%.2f) - %s [%s]"%(str(tt), d, tt.translations['fr'], ', '.join(t.relations.to(tt))))

mat_distance3 = None

def _table_entry(t):
    table = Table(t)
    return {
        'table': table,
        'term': t,
        'ss_set': set(t.script.singular_sequences)
    }


# layer -> rank -> terms[]
layers_by_rank = {
    i: {k: [_table_entry(t) for t in g]
        for k, g in groupby(sorted([t for t in layer if t.ntable == 1 and len(t) != 1], key=lambda t: t.rank), key=lambda t: t.rank)}
            for i, layer in enumerate(Dictionary().layers)
}


def _get_greater_common_rank(t0, t1):
    ranks = layers_by_rank[t0.layer]
    max_rank = max(ranks)

    ss_set = set(t0.script.singular_sequences).union(t1.script.singular_sequences)

    for i in range(max_rank, -1, -1):
        if i not in ranks:
            continue

        if any(ss_set.issubset(tt['ss_set']) for tt in ranks[i]):
            return float(max(i, 1)) / max_rank

    return 1.0/5.0
    # raise ValueError("No rank candidate found")


def _order(t0, t1):
    return (t0, t1) if t0 < t1 else (t1, t0)

C = .9

_siblings = {
    'opposed': 2, 'crossed': 1, 'associated': 3, 'twin': 0
}

def _get_sibling(t0, t1):
    return max(map(lambda r: _siblings[r], t0.relations.to(t1, ['opposed', 'crossed', 'associated', 'twin']))) + .5


def _distance_same_layer(t0, t1):
    t0, t1 = _order(t0, t1)

    if t0.layer != t1.layer:
        raise ValueError("Nop nop different layer")

    if t0 == t1:
        return 1.0

    if t0.root == t1.root:
        # siblings
        if t1 in t0.relations.siblings:
            return C + (1.0 - C) * float(_get_sibling(t0, t1)) / 4.0

        # table

        return C * _get_greater_common_rank(t0, t1)

    return 0.0


def _distance_upper_layer(t0, t1):
    t0, t1 = _order(t0, t1)

    if isinstance(t1.script, MultiplicativeScript):
        a, b, c = t1.script.children

        t_a = term(a)

        if isinstance(c, NullScript):
            if isinstance(b, NullScript):
                return mat_distance3[t0.index, t_a.index]
            else:
                t_b = term(b)

                return 0.6 * mat_distance3[t0.index, t_a.index] + \
                       0.4 * mat_distance3[t0.index, t_b.index]
        else:
            t_b = term(b)
            t_c = term(c)

            return 0.5 * mat_distance3[t0.index, t_a.index] + \
                   0.3 * mat_distance3[t0.index, t_b.index] + \
                   0.2 * mat_distance3[t0.index, t_c.index]
    elif isinstance(t1.script, AdditiveScript):
        res = [_distance_upper_layer(t0, term(s)) for s in t1.script]

        return sum(res) / len(res)


def _distance_upper_layer2(t0, t1):
    if isinstance(t1.script, MultiplicativeScript):
        a, b, c = t1.script.children

        def _dist(s):
            if isinstance(s, NullScript):
                return 0.0

            try:
                return mat_distance3[t0.index, term(s).index]
            except TermNotFoundInDictionary:
                return 0.0

        d_a = _dist(a)
        d_b = _dist(b)
        d_c = _dist(c)

        if isinstance(c, NullScript):
            if isinstance(b, NullScript):
                return 1.0 * d_a
            else:
                return 0.60 * d_a + 0.35 * d_b
        else:
            return 0.55 * d_a + 0.30 * d_b + 0.10 * d_c

    elif isinstance(t1.script, AdditiveScript):
        res = [_distance_upper_layer2(t0, term(s)) for s in t1.script]

        return sum(res) / len(res)


def _compute_distance_3():
    global mat_distance3

    indexes_layers = {
        k: [t.index for t in g] for k, g in groupby(Dictionary(), key=lambda t: t.layer)
    }

    def _distance_all_layer(t0, t1):
        t0, t1 = _order(t0, t1)

        return np.dot(mat_distance3[t0.index, indexes_layers[t1.layer - 1]],
                      mat_distance3[indexes_layers[t1.layer - 1], t1.index])

    def _set_distance(t0, t1, dist):
        mat_distance3[t0.index, t1.index] = dist
        mat_distance3[t1.index, t0.index] = dist

    d = Dictionary()
    mat_distance3 = np.zeros(shape=[len(d)]*2, dtype=float)

    for root in d.roots:
        terms = root.relations.contains
        for i, t0 in enumerate(terms):
            for t1 in terms[i:]:
                _set_distance(t0, t1, _distance_same_layer(t0, t1))

    # same layer + 1
    # for i, layer0 in enumerate(d.layers[:MAX_LAYER - 1]):
    #     for t0 in layer0:
    #         for t1 in (tt for tt in d.rel('child', t0) if tt.layer == i + 1):
    #             _set_distance(t0, t1, _distance_upper_layer2(t0, t1))

    for j in range(1, MAX_LAYER):
        for i, layer0 in enumerate(d.layers[:MAX_LAYER - 1]):
            if i+j == len(d.layers):
                break

            for t0 in layer0:
                for t1 in (tt for tt in d.rel('child', t0) if tt.layer == i + j):
                    _set_distance(t0, t1, _distance_upper_layer2(t0, t1))

    # assert mat_distance3 == mat_distance3.transpose()

def load_distance3_matrix():
    global mat_distance3
    version = get_default_dictionary_version()
    FILE = '/tmp/distance_3_m_%s.npy'%str(version)

    if os.path.isfile(FILE):
        mat_distance3 = np.load(FILE)
    else:
        _compute_distance_3()
        np.save(FILE, mat_distance3)


def distance3(t0, t1):
    return mat_distance3[t0.index, t1.index]


def test_distance3(t):
    print("Distance from term %s -- %s"%(str(t), t.translations['fr']))

    other = sorted(((distance3(t, t1), t1) for t1 in Dictionary() if not t1.script.paradigm), reverse=True)
    kkk = [t for t in other]
    for d, tt in kkk[:30]:
        print("%s (%.2f) - %s [%s]"%(str(tt), d, tt.translations['fr'], ', '.join(t.relations.to(tt))))


def test_distance_same_layer(t):
    print("Distance from term %s -- %s"%(str(t), t.translations['fr']))

    other = sorted(((distance3(t, t1), t1) for t1 in Dictionary()), reverse=True)
    kkk = [t for t in other]
    for d, tt in kkk[:30]:
        print("%s (%.2f) - %s [%s]"%(str(tt), d, tt.translations['fr'], ', '.join(t.relations.to(tt))))


def ranking_from_term(term0, nb_terms=30):
    other = sorted((mat_distance3[term0.index, t1.index],
                    _nb_relations(term0, t1) ,t1) for t1 in term0.dictionary)

    return other[:nb_terms]


if __name__ == '__main__':
    # print(distance3(term(312), term(3112)))
    load_distance3_matrix()
    test_distance_same_layer(term("U:"))
