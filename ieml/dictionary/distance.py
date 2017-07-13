import os
from itertools import combinations, product, groupby

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
        return C * 1. / 4, RELATIONS_TYPES[reltype]
    elif reltype == 'opposed':
        return C * 1. / 2, RELATIONS_TYPES[reltype]
    elif reltype == 'crossed':
        return C * 3. / 4, RELATIONS_TYPES[reltype]
    elif reltype == 'twin':
        return C, RELATIONS_TYPES[reltype]
    elif reltype.startswith('table_'):
        i = int(reltype[6:7])
        # rank
        # available slot: 2, 4
        ratio = float(max_rank - i) / max_rank
        slot = 2 if ratio < 0.5 else 4
        return C + k + (1 - 2*k - C) * ratio, (slot, max_rank - i)
    else:
        #sam
        if len(reltype) == 1:
            return C + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype]
        elif len(reltype) == 2:
            return (1 + C - k) / 2 + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype]
        elif len(reltype) == 3:
            return 1 - k + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype]
        else:
            ValueError("Invalid relation %s"%str(reltype))



RELATIONS_TYPES = {
    'associated': (0, 1),
    'opposed': (0, 2),
    'crossed': (0, 3),
    'twin': (0, 4),
    'table_5': (4, 0),
    'table_4': (4, 1),
    'table_3': (4, 2),
    'table_2': (4, 3),
    'table_1': (4, 4),
    'table_0': (4, 5),
    **{''.join(s): (1 + 2*(i-1), j) for i in range(1, 4) for j, s in enumerate(product('sam', repeat=i))}
}


def _enumerate_ancestors(t, prefix=''):
    for k, v in t.relations.father.items():
        for t1 in v:
            # if t1 is layer 0, we include this etymology only if it is a direct father/child
            if t1.layer == 0 and len(prefix) != 0:
                continue

            yield (prefix + k, t1)

            if len(prefix) < 2:
                yield from _enumerate_ancestors(t1, prefix=prefix + k)


def build_matrix(version):
    d = Dictionary(version)
    relation_matrix = np.empty(shape=(len(d),) * 2,
                            dtype=[('distance', 'f4'),('slot', 'i4', (2,)), ('reltype', 'S16')])

    relation_matrix['reltype'] = 'none'
    relation_matrix['slot'] = (0, 0)
    relation_matrix['distance'] = 1.0

    for i in range(len(d)):
        relation_matrix[i, i] = (0.0, (0, 0), 'none')

    for root in d.roots:
        max_rank = max(t.rank for t in root.relations.contains if len(t) != 1) + 1

        for t0, t1 in combinations(root.relations.contains, 2):

            reltype = min({r for r in t0.relations.to(t1) if r not in ('contained', 'contains')},
                          key=lambda r: RELATIONS_TYPES[r])

            v, order = relation_value(reltype, max_rank=max_rank)
            relation_matrix[t0.index, t1.index] = (v, order, reltype)
            relation_matrix[t1.index, t0.index] = (v, order, reltype)

    for layer in d.layers:
        for t0 in layer:
            for prefix, t1 in _enumerate_ancestors(t0):
                v, order = relation_value(prefix)
                relation_matrix[t0.index, t1.index] = (v, order, prefix)
                relation_matrix[t1.index, t0.index] = (v, order, prefix)

    return relation_matrix


def distance_matrix(version):
    if os.path.isfile('/tmp/cache_relations_%s.npy'%str(version)):
        return np.load('/tmp/cache_relations_%s.npy'%str(version))
    else:
        mat = build_matrix(version)
        np.save('/tmp/cache_relations_%s.npy'%str(version), mat)
        return mat


def default_metric(dictionary_version):
    mat = distance_matrix(dictionary_version)
    return lambda t0, t1: mat[t0.index, t1.index][0]


def distance_pack(t0, matrix):
    res = [(*matrix[t0.index, i], t0.dictionary.index[i]) for i in np.where(matrix['reltype'][t0.index, :] != b'none')[0]]
    res = sorted(res, key=lambda t: list(t[1]))

    return [(str(key, encoding='utf8'), [t[3] for t in v]) for key, v in groupby(res, key=lambda t: t[2])]


def rank_from_term(term, metric, nb_terms=30):
    res = sorted([(metric(term, t), t) for t in term.dictionary])[:nb_terms]
    return [r for r in res if r[0] != 1.0]


def test_metric(metric, t0, n=30):
    def _str_term(t):
        return "%s - (%s)"%(str(t), t.translations['fr'])

    print("distance from %s"%_str_term(t0))
    res = rank_from_term(t0, metric, nb_terms=n)

    print('\n'.join("[%.3f]: %s"%(r[0], _str_term(r[1])) for r in res))


