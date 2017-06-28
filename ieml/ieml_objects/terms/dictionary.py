import inspect
import json
from collections import defaultdict
from itertools import product, groupby
import itertools
from bidict import bidict
import numpy as np
import os

from scipy.sparse.csr import csr_matrix
from ieml.ieml_objects.terms.relations import RELATIONS
from ieml.ieml_objects.terms.version import DictionaryVersion, get_default_dictionary_version

from ieml.ieml_objects.terms import Term
from ieml.script.constants import MAX_LAYER
from ieml.script.operator import script
from ieml.script.script import AdditiveScript, NullScript, MultiplicativeScript
from ieml.config import DICTIONARY_FOLDER

class InvalidDictionaryState(Exception):
    def __init__(self, dictionary, message):
        self.dictionary = dictionary
        self.message = message

    def __str__(self):
        return "Invalid state dictionary state for version %s: %s"%(str(self.dictionary.version), self.message)


class DictionarySingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], (DictionaryVersion, str)):
            version = get_default_dictionary_version()
        elif isinstance(args[0], DictionaryVersion):
            version = args[0]
        elif isinstance(args[0], str):
            version = DictionaryVersion(args[0])
        else:
            raise ValueError("Invalid argument for dictionary creation, expected dictionary version, not %s"%str(args[0]))

        if version not in cls._instances:
            cls._instances[version] = super(DictionarySingleton, cls).__call__(version, **kwargs)

        return cls._instances[version]


class Dictionary(metaclass=DictionarySingleton):
    def __init__(self, version, cache=True, load=True):
        super().__init__()

        if isinstance(version, str):
            version = DictionaryVersion(version)

        self.version = version

        self.cache = cache

        # static elements from the version object
        self.terms = None
        self.translations = None
        self.roots = None
        self.inhibitions = None

        self.index = None

        # computed elements stored in cache
        # terms -> int
        self.ranks = None
        # terms -> terms[] all the terms that decompose the key into subtable
        self.partitions = None
        self.parents = None
        # numpy array
        self.relations = None

        # list layer (int) -> list of terms at this layer
        self._layers = None         # make layers stacks
        self._singular_sequences = None
        self._singular_sequence_map = None

        if load:
            self.load()

    @property
    def is_build(self):
        return all(getattr(self, attr) is not None for attr in ['terms', 'translations', 'roots', 'inhibitions',
                                                                'index', 'ranks', 'partitions', 'parents', 'relations'])

    def load(self):
        cache_folder = os.path.join(DICTIONARY_FOLDER, 'cache')
        cache_json = os.path.join(cache_folder, 'cache_%s.json'%(str(self.version)))
        cache_relations = os.path.join(cache_folder, 'cache_%s_relations.npy'%(str(self.version)))

        if not os.path.isdir(cache_folder):
            os.makedirs(cache_folder)

        if not os.path.isfile(cache_json) or not os.path.isfile(cache_relations) or not self.cache:
            if not self.is_build:
                self.build()

            if self.cache:
                print("\t[*] Saving dictionary cache to disk (%s, %s)" % (str(cache_json), str(cache_relations)))
                state = self.__getstate__()
                # save relations as numpy array
                np.save(arr=state['relations'], file=cache_relations)
                del state['relations']

                with open(cache_json, 'w') as fp:
                    json.dump(state, fp)
        else:
            print("\t[*] Loading dictionary from disk (%s, %s)" % (str(cache_json), str(cache_relations)))

            with open(cache_json, 'r') as fp:
                state = json.load(fp)

            state['relations'] = np.load(cache_relations)
            self.__setstate__(state)

        print("\t[*] Dictionary loaded (version: %s, nb_roots: %d, nb_terms: %d)"%
              (str(self.version), len(self.roots), len(self)))

    def build(self):
        self._populate()
        self.compute_ranks()
        self.compute_relations()

    @property
    def singular_sequences(self):
        if self._singular_sequences is None:
            self._singular_sequences = sorted(self.terms[ss] for r in self.roots for ss in r.script.singular_sequences)

        return self._singular_sequences

    @property
    def layers(self):
        if self._layers is None:
            self._layers = [[] for _ in range(MAX_LAYER + 1)]
            for t in self.index:
                self._layers[t.script.layer].append(t)

        return self._layers

    @property
    def singular_sequences_map(self):
        if self._singular_sequence_map is None:
            self._singular_sequence_map = {ss: r for r in self.roots for ss in r.script.singular_sequences}

        return self._singular_sequence_map

    def compute_ranks(self):
        print("\t[*] Computing ranks")
        tables = defaultdict(list)
        self.ranks = {}

        def get_rank_partition(term0, term1):
            def is_connexe_tilling(coords, t):
                shape_t = t.cells.shape
                # test if the table table is a connexe tiling of the table t
                size = 1
                for i, indexes in enumerate(zip(*coords)):
                    # if i >= t.dim:
                    #     return False

                    indexes = sorted(set(indexes))
                    size *= len(indexes)

                    missing = [j for j in range(shape_t[i]) if j not in indexes]
                    # more than one transition from missing -> included
                    transitions = [j for j in missing if (j + 1) % shape_t[i] not in missing]
                    if len(transitions) > 1:
                        step = int(shape_t[i] / len(transitions))

                        # check if there is a periodicity
                        if any((j + step)%shape_t[i] not in transitions for j in transitions):
                            return False

                    # at least a square of 2x2x1
                    if len(indexes) < 2 and i != 2:
                        return False

                if len(coords) == size:
                    return True

                return False

            def is_dim_subset(coords, t):
                """
                Return if it is a dim subset (only one dimension, the others are not touched)
                If True, return (True, nb_dim)
                else (False, 0)

                :param coords:
                :param t:
                :return:
                """
                shape_ts0 = tuple(len(set(indexes)) for indexes in zip(*coords))
                shape_t = t.cells.shape

                if shape_ts0[2] != shape_t[2]:
                    # subset of tabs, return True if no subset in row/columns
                    return shape_ts0[0] == shape_t[0] and shape_ts0[1] == shape_t[1], shape_ts0[2]

                if shape_ts0[0] == shape_t[0]:
                    return True, shape_ts0[1]

                if shape_ts0[1] == shape_t[1]:
                    return True, shape_ts0[0]

                return False, 0

            if term0.script not in term1.script or self.ranks[term1] % 2 == 0:
                return None, None

            if len(term0.script.tables) != 1:
                # the paradigm is split between tables (weird case)
                # in this case, term0 can be a subset of tabs of each table of term1
                # its must match the tabs headers of term1 tables
                for t1 in term1.script.tables:
                    for t0 in term0.script.tables:
                        if len(t0.headers) != 1:
                            raise ValueError()

                        h = next(t0.headers.__iter__())

                        if h in t1.headers:
                            break
                    else:
                        break
                else:
                    # print("Tabs subset for %s in %s"%(str(term0), str(term1)))
                    return 0, None

            for table in tables[term1]:
                if term0.script not in table.paradigm:
                    continue

                coords = sorted(table.index(term0.script))

                is_dim, count = is_dim_subset(coords, table)
                if is_dim and (count == 1 or table.dim == 1):
                    # one dimension subset, it is a rank 3/5 paradigm
                    return 2, table

                # the coordinates sorted of the ss of s0 in the table t
                # rank is then 2/4
                if is_connexe_tilling(coords, table) or is_dim:
                    return 1, table
            return None, None

        def _define(term, rank, term_src, defined):
            self.ranks[term] = rank

            defined.add(term)
            self.partitions[term_src].add(term)
            self.parents[term] = term_src

            for t in term.script.tables:
                t_term = self.terms[t.paradigm]
                tables[t_term] += [t]

                self.ranks[t_term] = rank
                defined.add(t_term)
                self.partitions[term_src].add(t_term)
                self.parents[t_term] = term_src

                if len(t.headers) != 1:
                    for tab in t.headers:
                        self.ranks[self.terms[tab]] = rank
                        defined.add(self.terms[tab])
                        tables[self.terms[tab]] = self.terms[tab].tables
                        self.partitions[term_src].add(self.terms[tab])
                        self.parents[self.terms[tab]] = term_src

        self.partitions = defaultdict(set)
        self.parents = {}
        for ss in self.singular_sequences:
            self.ranks[ss] = 6

        for root in self.roots:
            defined = set()
            _define(root, 1, root, defined)

            # order by the cardinal (ieml order reversed)
            for term in sorted(self.roots[root], reverse=True)[1:]:
                if term in defined:
                    continue

                if not term.script.paradigm:
                    break

                res = defaultdict(list)
                for term1 in defined:
                    rank, parent_table = get_rank_partition(term, term1)
                    if rank is not None:
                        res[self.ranks[term1] + rank].append(term1)

                if not res:
                    raise ValueError("No rank candidates for %s" % str(term))
                if len(res) > 1:
                    # print("Multiple rank candidates for %s (%s)" %
                    #                  (str(term), ', '.join("%s:%d->%d"%(str(t1), self.ranks[t1], r) for r,v in res.items() for parent_t, t1 in v)))
                    print("Multiple rank candidates [%s] for the term %s. Choosing the maximum rank."%(", ".join(["%d/%s"%(r, str(t[0].script)) for r, t in res.items()]), str(term)))
                    m = max(res)
                    res = {m: res[m]}

                rank = next(res.__iter__())
                if len(res[rank]) > 1:
                    res[rank] = sorted(res[rank])
                    print("Multiple candidate for parent of %s with rank %d : [%s]. Choosing 1st one."%(str(term), rank, ", ".join(str(t) for t in res[rank])))
                term1 = res[rank][0]

                _define(term, rank, term1, defined)

            self.ranks[root] = 0

    def __len__(self):
        return len(self.terms)

    def __contains__(self, item):
        return script(item) in self.terms

    def __iter__(self):
        return self.index.__iter__()

    def get_root(self, script):
        try:
            res = {self.singular_sequences_map[ss] for ss in script.singular_sequences}
        except KeyError:
            return None

        if len(res) > 1:
            raise ValueError("Script %s is in multiples root paradigms [%s]" % (str(script), ', '.join(map(str, res))))

        return next(res.__iter__())

    def rel(self, type, term=None):
        if term:
            return [self.index[j] for j in self.relations[RELATIONS.index(type)][term.index, :].indices]
        else:
            return self.relations[RELATIONS.index(type)][:, :]

    def relations_graph(self, relations_types):
        if isinstance(relations_types, dict):
            res = np.zeros((len(self), len(self)), dtype=np.float)
            for reltype in relations_types:
                res += self.relations[RELATIONS.index(reltype)] * relations_types[reltype]
            return res

        return np.sum([self.relations[RELATIONS.index(reltype)] for reltype in relations_types])

    def compute_relations(self):
        print("\t[*] Computing relations")

        for i, t in enumerate(self.index):
            t.index = i

        _relations = {}
        contains = self._compute_contains()
        _relations['contains'] = contains
        _relations['contained'] = np.transpose(_relations['contains'])

        father = self._compute_father()

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            _relations['father' + r] = father[i, :, :]
            # _relations['child' + r] = children[i, :, :]

        siblings = self._compute_siblings()
        _relations['opposed'] = siblings[0]
        _relations['associated'] = siblings[1]
        _relations['crossed'] = siblings[2]
        _relations['twin'] = siblings[3]

        self._do_inhibitions(_relations)

        for i, r in enumerate(['_substance', '_attribute', '_mode']):
            _relations['child' + r] = np.transpose(_relations['father' + r])

        _relations['siblings'] = sum(siblings)
        _relations['inclusion'] = np.clip(_relations['contains'] + _relations['contained'], 0, 1)
        _relations['father'] = _relations['father_substance'] + _relations['father_attribute'] + _relations['father_mode']
        _relations['child'] = _relations['child_substance'] + _relations['child_attribute'] + _relations['child_mode']
        _relations['etymology'] = _relations['father'] + _relations['child']

        _relations['table'] = np.zeros((len(self), len(self)), dtype=np.float32)
        for i, t in enumerate(self._compute_table_rank()):
            _relations['table_%d'%i] = t
            _relations['table'] = np.maximum((i + 1.0) * t, _relations['table'])

        missing = {s for s in RELATIONS if s not in _relations}
        if missing:
            raise ValueError("Missing relations : {%s}"%", ".join(missing))

        self.relations = []
        for reltype in RELATIONS:
            self.relations.append(csr_matrix(_relations[reltype]))

    def _compute_table_rank(self):
        print("\t\t[*] Computing tables relations")

        _tables_rank = np.zeros((6, len(self), len(self)))

        for i, t in enumerate(self.index):
            if t.script.paradigm and len(t.script.tables) == 1 and t.script.tables[0].dim < 3:

                contained_ss = [self.terms[ss].index for ss in t.script.singular_sequences]
                index0, index1 = list(zip(*product(contained_ss, repeat=2)))
                _tables_rank[t.rank, index0, index1] = 1

                h = t.script.tables[0].headers[t.script]
                contained_r_c = [self.terms[s].index for s in itertools.chain(h.rows, h.columns) if s in self.terms]

                if contained_r_c:
                    index0, index1 = list(zip(*product(contained_r_c, repeat=2)))
                    _tables_rank[t.rank, index0, index1] = 1

        for root in self.roots:
            indexes = [p.index for p in self.roots[root]]
            index0, index1 = list(zip(*product(indexes, repeat=2)))
            _tables_rank[0, index0, index1] = 1

        return _tables_rank

    def _do_inhibitions(self, _relations):
        print("\t\t[*] Performing inhibitions")

        for r in self.roots:
            inhibitions = self.inhibitions[r]
            indexes = [t.index for t in self.roots[r]]
            # index0, index1 = list(zip(*product(indexes, repeat=2)))

            for rel in inhibitions:
                _relations[rel][indexes, :] = 0

    def _compute_contains(self):
        print("\t\t[*] Computing contains/contained relations")
        # contain/contained
        contains = np.diag(np.ones(len(self), dtype=np.int8))
        for r_p, v in self.roots.items():
            paradigms = {t for t in v if t.script.paradigm}

            for p in paradigms:
                _contains = [self.terms[ss].index for ss in p.script.singular_sequences] + \
                           [k.index for k in paradigms if k.script in p.script]
                contains[p.index, _contains] = 1

        return contains

    def _compute_father(self):
        print("\t\t[*] Computing father/child relations")

        def _recurse_script(script, res_indexes, depth):
            if isinstance(script, NullScript):
                return

            if script in self.terms:
                depth += 1
                res_indexes.append((self.terms[script].index, depth))

            if script.layer == 0:
                return

            for c in script.children:
                _recurse_script(c, res_indexes, depth)

        father = np.zeros((3, len(self), len(self)), dtype=np.float32)
        for t in self.terms.values():
            s = t.script

            for sub_s in s if isinstance(s, AdditiveScript) else [s]:
                if len(sub_s.children) == 0 or isinstance(sub_s, NullScript):
                    continue

                for i in range(3):
                    res_indexes = []
                    _recurse_script(sub_s.children[i], res_indexes, 0)
                    for j, d in res_indexes:
                        father[i, t.index, j] = 1.0/d**2

        return father

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
                   _opposed_sibling(s0.children[0], s1.children[1]) and \
                   _opposed_sibling(s0.children[1], s1.children[0])

        siblings = np.zeros((4, len(self), len(self)), dtype=np.int8)

        print("\t\t[*] Computing siblings relations")

        for root in self.roots:
            if root.script.layer == 0:
                continue
            _twins = []

            for i, t0 in enumerate(self.roots[root]):
                if not isinstance(t0.script, MultiplicativeScript):
                    continue

                if t0.script.children[0] == t0.script.children[1]:
                    _twins.append(t0)

                for t1 in [t for j, t in enumerate(self.roots[root])
                           if j > i and isinstance(t.script, MultiplicativeScript)]:
                    if _opposed_sibling(t0.script, t1.script):
                        siblings[0, t0.index, t1.index] = 1
                        siblings[0, t1.index, t0.index] = 1

                    if _associated_sibling(t0.script, t1.script):
                        siblings[1, t0.index, t1.index] = 1
                        siblings[1, t1.index, t0.index] = 1

                    if _crossed_sibling(t0.script, t1.script):
                        siblings[2, t0.index, t1.index] = 1
                        siblings[2, t1.index, t0.index] = 1

            _twins = sorted(_twins, key=lambda t: t.script.cardinal)
            for card, g in groupby(_twins, key=lambda t: t.script.cardinal):
                twin_indexes = [t.index for t in g]

                if len(twin_indexes) > 1:
                    index0, index1 = list(zip(*product(twin_indexes, repeat=2)))
                    siblings[3, index0, index1] = 1

        return siblings

    def __getstate__(self):
        return {
            'relations': self.relations,
            'ranks': {str(t.script): r for t, r in self.ranks.items()},
            'partitions': {str(t.script): [str(tt.script) for tt in v] for t, v in self.partitions.items()},
            'parents': {str(t0.script): str(t1.script) for t0, t1 in self.parents.items()}
        }

    def __setstate__(self, state):
        self._populate(partitions=state['partitions'], ranks=state['ranks'], relations=state['relations'],
                       parents=state['parents'])

    def _populate(self, partitions=None, ranks=None, relations=None, parents=None):
        self.version.load()

        self.terms = {s: Term(s, dictionary=self) for s in self.version.terms}
        self.index = sorted(self.terms.values())

        for i, t in enumerate(self.index):
            t.index = i

        self.translations = {l: bidict({self.terms[t]: text for t, text in v.items()}) for l, v in
                             self.version.translations.items()}

        self.inhibitions = {self.terms[r]: v for r, v in self.version.inhibitions.items()}

        # if any(v for v in self.inhibitions.values()):
        #     raise InvalidDictionaryState("")

        self.roots = {self.terms[r]: [] for r in self.version.roots}

        try:
            for t in self.terms.values():
                self.roots[self.singular_sequences_map[t.script.singular_sequences[0]]].append(t)
        except KeyError as e:
            raise InvalidDictionaryState(self, "No root paradigm for script %s"%str(e.args[0]))

        if partitions is not None:
            self.partitions = defaultdict(set)
            for t, v in partitions.items():
                self.partitions[self.terms[t]] = {self.terms[tt] for tt in v}

        if ranks is not None:
            self.ranks = {}
            for t in self.index:
                self.ranks[t] = ranks[str(t.script)]

        if relations is not None:
            self.relations = relations

        if parents is not None:
            self.parents = {self.terms[t0]: self.terms[t1] for t0, t1 in parents.items()}

        # reset the cache properties
        self._layers = None
        self._singular_sequences = None

if __name__ == '__main__':
    # version = DictionaryVersion(datetime.date.today())
    # if False:
    #     d = Dictionary()
    #     version.terms = [str(t.script) for t in d.index]
    #     version.inhibitions = {str(t.script): v for t, v in d.inhibitions.items()}
    #     version.roots = [str(t.script) for t in d.roots]
    #     version.translations = {
    #         l: {
    #             str(t.script): trad for t, trad in v.items()
    #         } for l, v in d.translations.items()
    #     }
    #     version.upload_to_s3()

    Dictionary(DictionaryVersion()).build()

    # print(get_available_dictionary_version())

    # upload_dictionary_version(DictionaryVersion(datetime.date.today()))

    # get_dictionary_version("d")
    # Dictionary().build()
    # save_dictionary(DICTIONARY_FOLDER)
