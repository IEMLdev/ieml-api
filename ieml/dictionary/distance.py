import os
from itertools import combinations

import numpy as np

from ieml.dictionary.dictionary import Dictionary

#
# |____|____|____|____|______|_Ranks______________________|________|
# |Ass  Opp  Crss Twin|Father|         |GFather|          |GGFather|
# |                   |Child |         |GChild |          |GGChild |
# 0                   C     C+k        (1+C+-k)/2        1-k       1

# to set
C = 1./3
k = 1./8


def _sam_to_float(reltype):
    MAP = {'s':1, 'a':2, 'm': 3}
    res = 1.
    for c in reltype:
        res *= MAP[c] / 3.
    return res


def relation_value(reltype, max_rank=None):
    if reltype == 'associated':
        return C * 1. / 4
    elif reltype == 'opposed':
        return C * 1. / 2
    elif reltype == 'crossed':
        return C * 3. / 4
    elif reltype == 'twin':
        return C
    elif reltype.startswith('table_'):
        i = int(reltype[6:7])
        # rank
        return C + k + (1 - 2*k - C) * (max_rank - i) / max_rank
    else:
        #sam
        if len(reltype) == 1:
            return C + k * _sam_to_float(reltype)
        elif len(reltype) == 2:
            return (1 + C - k) / 2 + k * _sam_to_float(reltype)
        elif len(reltype) == 3:
            return 1 - k + k * _sam_to_float(reltype)
        else:
            ValueError("Invalid relation %s"%str(reltype))

RELATION_ORDER = {
    'associated': 0,
    'opposed': 1,
    'crossed': 2,
    'twin': 3,
    'table_5': 4,
    'table_4': 5,
    'table_3': 6,
    'table_2': 7,
    'table_1': 8,
    'table_0': 9
}


def _enumerate_ancestors(t, prefix=''):
    for k, v in t.relations.father.items():
        for t1 in v:
            yield (prefix + k, t1)

            if len(prefix) < 3:
                yield from _enumerate_ancestors(t1, prefix=prefix + k)


def build_matrix(version):
    d = Dictionary(version)
    relation_matrix = np.ones((len(d),) * 2, dtype=np.float32)

    for i in range(len(d)):
        relation_matrix[i, i] = 0.0

    for root in d.roots:
        max_rank = max(t.rank for t in root.relations.contains if len(t) != 1) + 1

        for t0, t1 in combinations(root.relations.contains, 2):

            reltype = min({r for r in t0.relations.to(t1) if r not in ('contained', 'contains')},
                          key=lambda r: RELATION_ORDER[r])

            v = relation_value(reltype, max_rank=max_rank)
            relation_matrix[t0.index, t1.index] = v
            relation_matrix[t1.index, t0.index] = v

    for layer in d.layers:
        for t0 in layer:
            for prefix, t1 in _enumerate_ancestors(t0):
                v = relation_value(prefix)
                relation_matrix[t0.index, t1.index] = v
                relation_matrix[t1.index, t0.index] = v

    return relation_matrix

def distance_matrix(version):
    if os.path.isfile('/tmp/cache_relations_%s.npy'%str(version)):
        return np.load('/tmp/cache_relations_%s.npy'%str(version))
    else:
        mat = build_matrix(version)
        np.save('/tmp/cache_relations_%s.npy'%str(version), mat)
        return mat

def test_metric(metric, t0, n=30):
    def _str_term(t):
        return "%s - (%s)"%(str(t), t.translations['fr'])

    print("distance from %s"%_str_term(t0))

    res = sorted([(metric(t0, t), t) for t in t0.dictionary])[:n]
    res = [r for r in res if r[0] != 1.0]
    print('\n'.join("[%.3f]: %s"%(r[0], _str_term(r[1])) for r in res))


