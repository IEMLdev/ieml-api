import os
import pickle
from enum import Enum, unique, IntEnum
from itertools import combinations, product, groupby, chain

import bidict
import numpy as np
from scipy.sparse.csr import csr_matrix

from ieml.dictionary.dictionary import Dictionary

def default_metric(dictionary_version):
    mat = get_matrix('distance', dictionary_version)
    return lambda t0, t1: mat[t0.index, t1.index]


def distance_pack(t0, version):
    reltypes = get_matrix('relation', version)
    distance = get_matrix('distance', version)

    res = [(reltypes[t0.index, i], t0.dictionary.index[i]) for i in reltypes[t0.index, :].indices]
    res = sorted(res, key=lambda t: t[0])

    return [(RelationType(key).name, [t[1] for t in v]) for key, v in groupby(res, key=lambda t: t[0])]


def rank_from_term(term, metric, nb_terms=30):
    res = sorted([(metric(term, t), t) for t in term.dictionary], reverse=True)[:nb_terms]
    return [r for r in res if r[0] if r[0] != 1.0]


def test_metric(metric, t0, n=30):
    def _str_term(t):
        return "%s - (%s)"%(str(t), t.translations['fr'])

    reltypes = get_matrix('relation', t0.dictionary.version)

    print("distance from %s"%_str_term(t0))
    res = rank_from_term(t0, metric, nb_terms=n)

    print('\n'.join("[%.3f] [%s]: %s"%(r[0], RelationType(reltypes[t0.index, r[1].index]).name,_str_term(r[1])) for r in res))




def get_matrix(name, version):
    file = '/tmp/cache_%s_%s.npy' % (name, str(version))
    if os.path.isfile(file):
        with open(file, 'rb') as fp:
            return pickle.load(fp)
    else:
        print("\t[*] Building distance matrix %s."%name)
        mat = MATRIX_BUILD[name](version)
        for k, v in mat.items():
            file_name = '/tmp/cache_%s_%s.npy' % (k, str(version))
            with open(file_name, 'wb') as fp:
                pickle.dump(v, fp)

        return mat[name]
# to set

#
# |____|____|____|____|______|_Ranks______________________|________|
# |Ass  Opp  Crss Twin|Father|         |GFather|          |GGFather|
# |                   |Child |         |GChild |          |GGChild |
# 0                   C     C+k        (1+C+-k)/2        1-k       1

def _relation_value(reltype, max_rank=None):
    C = 1. / 3
    k = 1. / 8

    def _sam_to_float(reltype):
        MAP = {'s': 1, 'a': 2, 'm': 3}
        res = 1.
        for c in reltype:
            res *= MAP[c] / 3.
        return res

    if reltype == 'Nll':
        return 0, RELATIONS_TYPES, RelationType.Null
    elif reltype == 'associated':
        return C * 1. / 4, RELATIONS_TYPES[reltype], RelationType.Associated
    elif reltype == 'opposed':
        return C * 1. / 2, RELATIONS_TYPES[reltype], RelationType.Opposed
    elif reltype == 'crossed':
        return C * 3. / 4, RELATIONS_TYPES[reltype], RelationType.Crossed
    elif reltype == 'twin':
        return C, RELATIONS_TYPES[reltype], RelationType.Twin
    elif reltype.startswith('table_'):
        i = int(reltype[6:7])
        # rank
        # available slot: 2, 4
        ratio = float(max_rank - i) / max_rank
        slot = 2 if ratio < 0.5 else 4
        return C + k + (1 - 2*k - C) * ratio, (slot, max_rank - i), RelationType['Rank_%d'%i]
    else:
        #sam
        if len(reltype) == 1:
            return C + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype], RelationType['Etymology_%s'%reltype]
        elif len(reltype) == 2:
            return (1 + C - k) / 2 + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype], RelationType['Etymology_%s'%reltype]
        elif len(reltype) == 3:
            return 1 - k + k * _sam_to_float(reltype), RELATIONS_TYPES[reltype], RelationType['Etymology_%s'%reltype]
        else:
            ValueError("Invalid relation %s"%str(reltype))


def _build_distance_matrix(version):
    def _enumerate_ancestors(t, prefix=''):
        for k, v in t.relations.father.items():
            for t1 in v:
                # if t1 is layer 0, we include this etymology only if it is a direct father/child
                if t1.layer == 0 and len(prefix) != 0:
                    continue

                yield (prefix + k, t1)

                if len(prefix) < 2:
                    yield from _enumerate_ancestors(t1, prefix=prefix + k)


    d = Dictionary(version)
    # relation_matrix = np.empty(shape=(len(d),) * 2,
    #                         dtype=[('distance', 'f4'),('slot', 'i4', (2,)), ('reltype', 'S16')])

    distance_matrix = np.empty(shape=(len(d),) * 2, dtype='f4')
    order_matrix = np.empty(shape=(len(d),) * 2, dtype='i4')
    relation_type_matrix = np.empty(shape=(len(d),) * 2, dtype='i4')

    # relation_matrix['reltype'] = 'none'
    # relation_matrix['slot'] = (0, 0)
    # relation_matrix['distance'] = 1.0

    for root in d.roots:
        max_rank = max(t.rank for t in root.relations.contains if len(t) != 1) + 1

        for t0, t1 in combinations(root.relations.contains, 2):

            reltype = min({r for r in t0.relations.to(t1) if r not in ('contained', 'contains')},
                          key=lambda r: RELATIONS_TYPES[r])


            v, order, reltype = _relation_value(reltype, max_rank=max_rank)
            distance_matrix[t0.index, t1.index] = 1 - v
            order_matrix[t0.index, t1.index] = order[0] * 100 + order[1]
            relation_type_matrix[t0.index, t1.index] = int(reltype)

    for layer in d.layers:
        for t0 in layer:
            for prefix, t1 in _enumerate_ancestors(t0):
                v, order, reltype = _relation_value(prefix)
                distance_matrix[t0.index, t1.index] = 1 - v
                order_matrix[t0.index, t1.index] = order[0] * 100 + order[1]
                relation_type_matrix[t0.index, t1.index] = int(reltype)

    distance_matrix = distance_matrix + distance_matrix.transpose()
    order_matrix = order_matrix + order_matrix.transpose()
    relation_type_matrix = relation_type_matrix + relation_type_matrix.transpose()

    for i in range(len(d)):
        distance_matrix[i, i] = 1.0
        order_matrix[i, i] = 0
        relation_type_matrix[i, i] = int(RelationType.Equal)

    distance_matrix = csr_matrix(distance_matrix)
    order_matrix = csr_matrix(order_matrix)
    relation_type_matrix = csr_matrix(relation_type_matrix)

    return {'distance' : distance_matrix,
            'order': order_matrix,
            'relation': relation_type_matrix}





# Ordre sur les relations:
# Class principals :
# Ass > Opp > Crs > Twn > Fth > Rnk > Chd > Nll
# Sous-class
# Fth/Chd :
# S > A > M > SS > SA ...
# Rnk:
# 5 > 4 ... > 0


def _enumerate_ancestors(t, prefix=''):
    for k, v in t.relations.father.items():
        for t1 in v:
            # if t1 is layer 0, we include this etymology only if it is a direct father/child
            if t1.layer == 0 and len(prefix) != 0:
                continue

            yield (prefix + k, t1)
            yield from _enumerate_ancestors(t1, prefix=prefix + k)


def _build_ancestor_matrix(version):
    d = Dictionary(version)
    matrix = np.empty(shape=(len(d),) * 2, dtype=[('relation', "U8"), ('prefix', "U8")])

    for layer in d.layers:
        for t0 in layer:
            for prefix, t1 in _enumerate_ancestors(t0):
                matrix[t0.index, t1.index]['relation'] = 'Fth'
                matrix[t0.index, t1.index]['prefix'] = prefix

                matrix[t1.index, t0.index]['relation'] = 'Chd'
                matrix[t1.index, t0.index]['prefix'] = prefix

    return {'ancestor': matrix}


MATRIX_BUILD = {
    'distance': _build_distance_matrix,
    'order': _build_distance_matrix,
    'relation': _build_distance_matrix,
    'ancestor': _build_ancestor_matrix
}



# index to order
# 1st main
# 0 <= 2nd < 100
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


RelationType = unique(IntEnum('RelationType', {
    'Null': 0,
    'Equal': 1,
    'Crossed': 2,
    'Associated': 3,
    'Twin': 4,
    'Opposed': 5,
    **{'Rank_%d'%i: 6 + i  for i in range(6)},
    **{'Etymology_%s'%''.join(s): int(11 + (3 ** i - 1) / 2 + j) for i in range(1, 4) for j, s in enumerate(product('sam', repeat=i))}
}))


RELATION_ORDER_FROM_MAX_RANK = {
    i: ['Equal', 'Associated', 'Opposed', 'Crossed', 'Twin', 'Father'] for i in range(6)
}

# RELATION_ORDER_FROM_MAX_RANK[0] += ['Rank_0', 'Child', 'FatherFather', 'ChildChild', 'FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[0] += ['Rank_0', 'Child', 'FatherFather', 'ChildChild', 'FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[1] += ['Rank_1', 'Child', 'FatherFather', 'ChildChild', 'Rank_0','FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[2] += ['Rank_2', 'Child', 'FatherFather', 'Rank_1', 'ChildChild', 'Rank_0', 'FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[3] += ['Rank_3', 'Child', 'Rank_2', 'FatherFather', 'Rank_1', 'ChildChild', 'Rank_0', 'FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[4] += ['Rank_4', 'Child', 'Rank_3', 'Rank_2', 'FatherFather', 'Rank_1', 'ChildChild', 'Rank_0', 'FatherFatherFather', 'ChildChildChild']
RELATION_ORDER_FROM_MAX_RANK[5] += ['Rank_5', 'Child', 'Rank_4', 'Rank_3', 'Rank_2', 'FatherFather', 'Rank_1', 'ChildChild', 'Rank_0', 'FatherFatherFather', 'ChildChildChild']




# class RelationTerm:
#     ancestor = None
#     def __init__(self, term0, term1):
#         if self.ancestor is None:
#             self.__class__.ancestor = get_matrix('ancestor', term0.dictionary.version)
#
#         self.t0 = term0
#         self.t1 = term1
#         if self.t0 == self.t1:
#             self.relation_type = 'Idt'
#             self.order = 0
#
#         elif self.t0.root == self.t1.root:
#             self.relation_type = min({r for r in self.t0.relations.to(self.t1) if r not in ('contained', 'contains')},
#                           key=lambda r: RELATIONS_TYPES[r])
#
#             self.order = RELATIONS_TYPES[self.relation_type]
#         elif self.ancestor[self.t0.index, self.t1.index]['relation'] != '' and\
#              len(self.ancestor[self.t0.index, self.t1.index]['prefix']) < 4:
#             self.relation_type, self.subtype = self.ancestor[self.t0.index, self.t1.index]
#
#             self.order = RELATIONS_TYPES[self.subtype]
#         else:
#             self.relation_type = 'Nll'
#             _, self.order = _relation_value('Nll')
#
#     def __eq__(self, other):
#         return {self.t0, self.t1} == {other.t0, other.t1}
#
#     def __lt__(self, other):
#         return self.order < other.order
#
#     def __str__(self):
#         return _RELATION_TYPES[self.relation_type]['name']
#
