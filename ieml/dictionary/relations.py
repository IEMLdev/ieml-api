import logging
from collections import OrderedDict, defaultdict
from itertools import groupby, combinations, permutations, chain, repeat

import numpy as np
from scipy.sparse.coo import coo_matrix
from scipy.sparse.csr import csr_matrix
from scipy.sparse.dok import dok_matrix

from ieml.commons import cached_property
from ieml.dictionary.script.script import MultiplicativeScript, AdditiveScript, NullScript

logger = logging.getLogger(__name__)
RELATIONS = [
            'contains',         # 0
            'contained',        # 1
            'father_substance', # 2
            'child_substance',  # 3
            'father_attribute', # 4
            'child_attribute',  # 5
            'father_mode',      # 6
            'child_mode',       # 7
            'opposed',          # 8
            'associated',       # 9
            'crossed',          # 10
            'twin',             # 11
            'table_0',
            'table_1',
            'table_2',
            'table_3',
            'table_4',
            'table_5',

             # 'inclusion',        # 12
             # 'father',           # 13
             # 'child',            # 14
             # 'etymology',        # 15
             # 'siblings',         # 16
             # 'table'             # 17
             ]

INVERSE_RELATIONS = {
    'father_substance': 'child_substance',
    'child_substance': 'father_substance',  # 3
    'father_attribute': 'child_attribute', # 4
    'child_attribute': 'father_attribute',  # 5
    'father_mode': 'child_mode',      # 6
    'child_mode': 'father_mode',
    'contains': 'contained',
    'contained': 'contains',
    'opposed':'opposed',          # 8
    'associated':'associated',       # 9
    'crossed': 'crossed',        # 10
    'twin': 'twin',
    'table_0': 'table_0',
    'table_1': 'table_1',
    'table_2': 'table_2',
    'table_3': 'table_3',
    'table_4': 'table_4',
    'table_5': 'table_5',
    'father': 'child',
    'child': 'father',
    'inclusion': 'inclusion',
    'etymology': 'etymology',        # 15
    'siblings': 'siblings',         # 16
    'table': 'table'
}


class RelationsGraph:
    def __init__(self, dictionary):
        super().__init__()

        self.dictionary = dictionary
        self.relations = None
        self._compute_relations()

    def __getitem__(self, item):
        if isinstance(item, str) and item in RELATIONS:
            return self.relations[item]

        if isinstance(item, int):
            return self.relations[RELATIONS[item]]

        from .terms import Term
        if isinstance(item, Term):
            if item.dictionary != self.dictionary:
                raise ValueError("Invalid dictionary, (%s/%s)"%(str(item.dictionary), str(self.dictionary)))
            return Relations(term=item, relations_graph=self)

        raise NotImplemented

    @cached_property
    def connexity(self):
        """
        A boolean matrix, m[i, j] == True if there is a relation term(i) -> term(j)
        :return: a np.matrix (len(dictionary), len(dictionary)) of boolean
        """
        return np.matrix(sum(self.relations.values()).todense(), dtype=bool)

    def relation_type(self, term, relation_type):
        return [self.dictionary.index[j] for j in
                self.relations[relation_type][term.index, :].indices]

    def neighbours(self, term):
        return {
            reltype: self.relation_type(term, reltype) for reltype in RELATIONS
        }

    def _compute_relations(self):
        logger.log(logging.INFO, "Computing relations")

        self.relations = {}
        contains = self._compute_contains()
        self.relations['contains'] = csr_matrix(contains)
        self.relations['contained'] = csr_matrix(self.relations['contains'].transpose())

        father = self._compute_father()

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            self.relations['father' + r] = dok_matrix(father[i])

        siblings = self._compute_siblings()
        self.relations['opposed'] = dok_matrix(siblings[0])
        self.relations['associated'] = dok_matrix(siblings[1])
        self.relations['crossed'] = dok_matrix(siblings[2])
        self.relations['twin'] = dok_matrix(siblings[3])

        # self._do_inhibitions()

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            self.relations['child' + r] = self.relations['father' + r].transpose()

        # self.relations['siblings'] = sum(siblings)
        # self.relations['inclusion'] = np.clip(self.relations['contains'] + self.relations['contained'], 0, 1)
        # self.relations['father'] = self.relations['father_substance'] + \
        #                            self.relations['father_attribute'] + \
        #                            self.relations['father_mode']
        # self.relations['child'] = self.relations['child_substance'] + \
        #                           self.relations['child_attribute'] + \
        #                           self.relations['child_mode']
        # self.relations['etymology'] = self.relations['father'] + self.relations['child']

        table = self._compute_table_rank(self.relations['contained'])
        for i in range(6):
            self.relations['table_%d'%i] = table[i]

        missing = {s for s in RELATIONS if s not in self.relations}
        if missing:
            raise ValueError("Missing relations : {%s}"%", ".join(missing))

        self.relations = {reltype: csr_matrix(self.relations[reltype]) for reltype in RELATIONS}

    def _compute_table_rank(self, contained):
        logger.log(logging.DEBUG, "Computing tables relations")

        tables_rank = [([], []) for _ in range(6)]

        indices = [
            set(l) for l in np.split(contained.indices, contained.indptr)[1:-1]
        ]

        for root in self.dictionary.roots:
            for t0, t1 in combinations(self.dictionary.roots[root], 2):
                commons = [self.dictionary.index[i] for i in indices[t0.index] & indices[t1.index]]

                rank = max(map(lambda t: t.rank, commons))
                tables_rank[rank][0].extend((t0.index, t1.index))
                tables_rank[rank][1].extend((t1.index, t0.index))

        return [coo_matrix(([True]*len(i), (i, j)), shape=self.shape, dtype=np.bool) for i, j in tables_rank]

    def _compute_contains(self):
        logger.log(logging.DEBUG, "Computing contains/contained relations")
        # contain/contained

        i = list(range(len(self.dictionary)))
        j = list(range(len(self.dictionary)))
        for r_p, v in self.dictionary.roots.items():
            paradigms = {t for t in v if t.script.paradigm}

            for p in paradigms:
                _contains = [self.dictionary.terms[ss].index for ss in p.script.singular_sequences] + \
                            [k.index for k in paradigms if k.script in p.script]
                i.extend(repeat(p.index, len(_contains)))
                j.extend(_contains)

        return coo_matrix(([True] * len(i), (i, j)), shape=self.shape, dtype=np.bool)

    def _compute_father(self):
        logger.log(logging.DEBUG, "Computing father/child relations")

        def _recurse_script(script):
            result = []
            for sub_s in script.children if isinstance(script, AdditiveScript) else [script]:
                if isinstance(sub_s, NullScript):
                    continue

                if sub_s in self.dictionary.terms:
                    result.append(self.dictionary.terms[sub_s].index)
                else:
                    if sub_s.layer > 0:
                        result.extend(chain.from_iterable(_recurse_script(c) for c in sub_s.children))

            return result

        # father = coo_matrix((3, len(self.dictionary), len(self.dictionary)), dtype=np.bool)

        father = [([], []) for _ in range(3)]

        for t in self.dictionary.terms.values():
            s = t.script

            for sub_s in s if isinstance(s, AdditiveScript) else [s]:
                if len(sub_s.children) == 0 or isinstance(sub_s, NullScript):
                    continue

                for i, s in enumerate(('father_substance', 'father_attribute', 'father_mode')):
                    if s in t.inhibitions:
                        continue

                    fathers_indexes = _recurse_script(sub_s.children[i])
                    father[i][0].extend(repeat(t.index, len(fathers_indexes)))
                    father[i][1].extend(fathers_indexes)

        return [coo_matrix(([True] * len(i), (i, j)), shape=self.shape, dtype=np.bool) for i, j in father]

    def _compute_siblings(self):
        # siblings
        # 1 dim => the sibling type
        #  -0 opposed
        #  -1 associated
        #  -2 crossed
        #  -3 twin
        def _opposed_sibling(s0, s1):
            return not s0.empty and not s1.empty and\
                   s0.cardinal == s1.cardinal and\
                   s0.children[0] == s1.children[1] and s0.children[1] == s1.children[0]

        def _associated_sibling(s0, s1):
            return s0.cardinal == s1.cardinal and\
                   s0.children[0] == s1.children[0] and \
                   s0.children[1] == s1.children[1] and \
                   s0.children[2] != s1.children[2]

        def _crossed_sibling(s0, s1):
            return s0.layer >= 2 and \
                   s0.cardinal == s1.cardinal and \
                   _opposed_sibling(s0.children[0], s1.children[0]) and \
                   _opposed_sibling(s0.children[1], s1.children[1])

        siblings = [([], []) for _ in range(4)]

        logger.log(logging.DEBUG, "Computing siblings relations")

        for root in self.dictionary.roots:
            _inhib_opposed = 'opposed' not in root.inhibitions
            _inhib_associated = 'associated' not in root.inhibitions
            _inhib_crossed = 'crossed' not in root.inhibitions
            _inhib_twin = 'twin' not in root.inhibitions

            if root.script.layer == 0:
                continue
            _twins = []

            for i, t0 in enumerate(self.dictionary.roots[root]):
                if not isinstance(t0.script, MultiplicativeScript):
                    continue

                if t0.script.children[0] == t0.script.children[1]:
                    _twins.append(t0)

                for t1 in [t for j, t in enumerate(self.dictionary.roots[root])
                           if j > i and isinstance(t.script, MultiplicativeScript)]:

                    if _inhib_opposed and _opposed_sibling(t0.script, t1.script):
                        siblings[0][0].extend((t0.index, t1.index))
                        siblings[0][1].extend((t1.index, t0.index))

                    if _inhib_associated and _associated_sibling(t0.script, t1.script):
                        siblings[1][0].extend((t0.index, t1.index))
                        siblings[1][1].extend((t1.index, t0.index))

                    if _inhib_crossed and _crossed_sibling(t0.script, t1.script):
                        siblings[2][0].extend((t0.index, t1.index))
                        siblings[2][1].extend((t1.index, t0.index))

            if _inhib_twin:
                _twins = sorted(_twins, key=lambda t: t.script.cardinal)
                for card, g in groupby(_twins, key=lambda t: t.script.cardinal):
                    twin_indexes = [t.index for t in g]

                    if len(twin_indexes) > 1:
                        index0, index1 = list(zip(*permutations(twin_indexes, r=2)))
                        siblings[3][0].extend(index0)
                        siblings[3][1].extend(index1)

        return [coo_matrix(([True]*len(i), (i, j)), shape=self.shape, dtype=np.bool) for i, j in siblings]

    @property
    def shape(self):
        return (len(self.dictionary), len(self.dictionary))

    def __setstate__(self, state):
        self.relations = state['relations']
        self.dictionary = state['dictionary']

    def __getstate__(self):
        return {
            'relations': self.relations,
            'dictionary': self.dictionary
        }


class Relations:
    def __init__(self, term, relations_graph):
        super().__init__()

        self.relations_graph = relations_graph
        self.term = term

    @cached_property
    def neighbours(self):
        rels = defaultdict(list)
        for reltype in RELATIONS:
            for t in self[reltype]:
                rels[t].append(reltype)

        neighbours = OrderedDict()

        for t in sorted(rels):
            neighbours[t] = rels[t]

        return neighbours

    def to(self, term, relations_types=None):
        if relations_types is None:
            relations_types = RELATIONS

        if term not in self.neighbours:
            return []

        return [reltype for reltype in self.neighbours[term] if reltype in relations_types]

    def __iter__(self):
        return self.neighbours.__iter__()

    def __len__(self):
        return len(self.neighbours)

    def __contains__(self, item):
        return item in self.neighbours

    def __getitem__(self, item):
        if isinstance(item, int):
            item = RELATIONS[item]

        if isinstance(item, str):
            return getattr(self, item)

        raise NotImplemented

    @property
    def father(self):
        return {
            's': self.father_substance,
            'a': self.father_attribute,
            'm': self.father_mode,
        }

    @property
    def child(self):
        return {
            's': self.child_substance,
            'a': self.child_attribute,
            'm': self.child_mode,
        }


def get_relation(reltype):
    def getter(self):
        return tuple(self.relations_graph.relation_type(term=self.term, relation_type=reltype))

    getter.__name__ = reltype
    return getter


for reltype in {'contains',
                'contained',
                'father_substance',
                'child_substance',
                'father_attribute',
                'child_attribute',
                'father_mode',
                'child_mode',
                'opposed',
                'associated',
                'crossed',
                'twin',
                'table_0',
                'table_1',
                'table_2',
                'table_3',
                'table_4',
                'table_5'}:
    setattr(Relations, reltype, cached_property(get_relation(reltype)))
