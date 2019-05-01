from itertools import groupby, combinations, permutations, chain, repeat

import numpy as np
import pandas

from scipy.sparse.coo import coo_matrix
from scipy.sparse.csr import csr_matrix
from scipy.sparse.dok import dok_matrix

from ieml.constants import RELATIONS
from ieml.dictionary.script.script import MultiplicativeScript, AdditiveScript, NullScript

class RelationsGraph:
    def __init__(self, dictionary):
        super().__init__()

        # dictionary = dictionary
        self.relations = self._compute_relations(dictionary)

        self.matrix = np.matrix(sum(self.relations.values()).todense())

        self.scripts = dictionary.scripts
        self.index = dictionary.index

    def object(self, subject, relation):
        return self.scripts[sorted(self.relations[relation][self.index[subject]].indices)]

    def relation_object(self, subject):
        return {relation: self.object(subject, relation) for relation in RELATIONS}

    def pandas(self):
        subjects = []
        relations = []
        objects = []
        for s in self.scripts:
            for r in RELATIONS:
                for o in self.object(s, r):
                    subjects.append(str(s))
                    relations.append(r)
                    objects.append(str(o))

        return pandas.DataFrame({
            'substance': subjects,
            'attribute': objects,
            'mode': relations
        })

    @property
    def boolean_matrix(self):
        """
        A boolean matrix, m[i, j] == True if there is a relation term(i) -> term(j)
        :return: a np.matrix (len(dictionary), len(dictionary)) of boolean
        """
        return np.matrix(self.matrix, dtype=bool)

    @staticmethod
    def _compute_relations(dictionary):
        # print("Computing relations", file=sys.stderr)
        # logger.log(logging.DEBUG, "Computing tables relations")
        # logger.log(logging.DEBUG, "Computing contains/contained relations")
        # logger.log(logging.DEBUG, "Computing father/child relations")
        # print("Computing siblings relations", sys.stderr)

        relations = {}
        contains = RelationsGraph._compute_contains(dictionary)
        relations['contains'] = csr_matrix(contains)
        relations['contained'] = csr_matrix(relations['contains'].transpose())

        father = RelationsGraph._compute_father(dictionary)

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            relations['father' + r] = dok_matrix(father[i])

        siblings = RelationsGraph._compute_siblings(dictionary)
        relations['opposed'] = dok_matrix(siblings[0])
        relations['associated'] = dok_matrix(siblings[1])
        relations['crossed'] = dok_matrix(siblings[2])
        relations['twin'] = dok_matrix(siblings[3])

        # self._do_inhibitions()

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            relations['child' + r] = relations['father' + r].transpose()

        # self.relations['siblings'] = sum(siblings)
        # self.relations['inclusion'] = np.clip(self.relations['contains'] + self.relations['contained'], 0, 1)
        # self.relations['father'] = self.relations['father_substance'] + \
        #                            self.relations['father_attribute'] + \
        #                            self.relations['father_mode']
        # self.relations['child'] = self.relations['child_substance'] + \
        #                           self.relations['child_attribute'] + \
        #                           self.relations['child_mode']
        # self.relations['etymology'] = self.relations['father'] + self.relations['child']

        table = RelationsGraph._compute_table_rank(dictionary, relations['contained'])
        for i in range(6):
            relations['table_%d'%i] = table[i]

        relations['identity'] = csr_matrix(np.eye(len(dictionary)))

        missing = {s for s in RELATIONS if s not in relations}
        if missing:
            raise ValueError("Missing relations : {%s}"%", ".join(missing))

        return {reltype: csr_matrix(relations[reltype]) for reltype in RELATIONS}

    @staticmethod
    def _compute_table_rank(dictionary, contained):

        tables_rank = [([], []) for _ in range(6)]

        indices = [
            set(l) for l in np.split(contained.indices, contained.indptr)[1:-1]
        ]

        for root in dictionary.tables.roots:

            for t0, t1 in combinations(dictionary.tables.roots[root], 2):
                i0 = dictionary.index[t0.script]
                i1 = dictionary.index[t1.script]

                commons = [dictionary.scripts[i] for i in indices[i0] & indices[i1]]
                ranks = set(map(lambda t: dictionary.tables.tables[t].rank, commons))
                for rank in ranks:
                    tables_rank[rank][0].extend((i0, i1))
                    tables_rank[rank][1].extend((i1, i0))

        for t in dictionary.scripts:
            idx = dictionary.index[t]
            ranks = {dictionary.tables.tables[dictionary.scripts[i]].rank for i in indices[idx]} - {6}
            for rank in ranks:
                tables_rank[rank][0].append(idx)
                tables_rank[rank][1].append(idx)

        shape = [len(dictionary)] * 2
        return [coo_matrix(([True]*len(i), (i, j)), shape=shape, dtype=np.bool) for i, j in tables_rank]

    @staticmethod
    def _compute_contains(dictionary):
        # contain/contained
        shape = [len(dictionary)] * 2

        i = list(range(shape[0]))
        j = list(range(shape[1]))

        for r_p, v in dictionary.tables.roots.items():
            paradigms = {t for t in v if t.script.paradigm}

            for p in paradigms:
                _contains = [dictionary.index[ss] for ss in p.script.singular_sequences] + \
                            [dictionary.index[k.script] for k in paradigms if k.script in p.script]
                i.extend(repeat(dictionary.index[p.script], len(_contains)))
                j.extend(_contains)

        return coo_matrix(([True] * len(i), (i, j)), shape=shape, dtype=np.bool)

    @staticmethod
    def _compute_father(dictionary):

        shape = [len(dictionary)] * 2
        scripts = set(dictionary.scripts)

        def _recurse_script(script):
            result = []
            for sub_s in script.children if isinstance(script, AdditiveScript) else [script]:
                if isinstance(sub_s, NullScript):
                    continue

                if sub_s in scripts:
                    result.append(dictionary.index[sub_s])
                else:
                    if sub_s.layer > 0:
                        result.extend(chain.from_iterable(_recurse_script(c) for c in sub_s.children))

            return result

        # father = coo_matrix((3, len(dictionary), len(dictionary)), dtype=np.bool)

        father = [([], []) for _ in range(3)]

        for s in dictionary.scripts:
            for sub_s in s if isinstance(s, AdditiveScript) else [s]:
                if len(sub_s.children) == 0 or isinstance(sub_s, NullScript):
                    continue

                for i, rel in enumerate(('father_substance', 'father_attribute', 'father_mode')):
                    if rel in dictionary._inhibitions:
                        continue

                    fathers_indexes = _recurse_script(sub_s.children[i])
                    father[i][0].extend(repeat(dictionary.index[s], len(fathers_indexes)))
                    father[i][1].extend(fathers_indexes)

        return [coo_matrix(([True] * len(i), (i, j)), shape=shape, dtype=np.bool) for i, j in father]

    @staticmethod
    def _compute_siblings(dictionary):
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

        for root in dictionary.tables.roots:
            _inhib_opposed = 'opposed' not in dictionary._inhibitions[root]
            _inhib_associated = 'associated' not in dictionary._inhibitions[root]
            _inhib_crossed = 'crossed' not in dictionary._inhibitions[root]
            _inhib_twin = 'twin' not in dictionary._inhibitions[root]

            if root.layer == 0:
                continue
            _twins = []

            for i, t0 in enumerate(dictionary.tables.roots[root]):
                if not isinstance(t0.script, MultiplicativeScript):
                    continue

                if t0.script.children[0] == t0.script.children[1]:
                    _twins.append(t0)

                for t1 in [t for j, t in enumerate(dictionary.tables.roots[root])
                           if j > i and isinstance(t.script, MultiplicativeScript)]:

                    i0 = dictionary.index[t0.script]
                    i1 = dictionary.index[t1.script]

                    if _inhib_opposed and _opposed_sibling(t0.script, t1.script):
                        siblings[0][0].extend((i0, i1))
                        siblings[0][1].extend((i1, i0))

                    if _inhib_associated and _associated_sibling(t0.script, t1.script):
                        siblings[1][0].extend((i0, i1))
                        siblings[1][1].extend((i1, i0))

                    if _inhib_crossed and _crossed_sibling(t0.script, t1.script):
                        siblings[2][0].extend((i0, i1))
                        siblings[2][1].extend((i1, i0))

            if _inhib_twin:
                _twins = sorted(_twins, key=lambda t: t.script.cardinal)
                for card, g in groupby(_twins, key=lambda t: t.script.cardinal):
                    twin_indexes = [dictionary.index[t.script] for t in g]

                    if len(twin_indexes) > 1:
                        index0, index1 = list(zip(*permutations(twin_indexes, r=2)))
                        siblings[3][0].extend(index0)
                        siblings[3][1].extend(index1)

        shape = [len(dictionary)] * 2
        return [coo_matrix(([True]*len(i), (i, j)), shape=shape, dtype=np.bool) for i, j in siblings]
