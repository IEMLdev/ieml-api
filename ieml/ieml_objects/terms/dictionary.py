import inspect
import json
from collections import defaultdict
from itertools import product, groupby, chain, combinations
import itertools
from bidict import bidict
import numpy as np
import os

from scipy.sparse.csr import csr_matrix
from ieml.ieml_objects.terms.relations import RELATIONS
from ieml.ieml_objects.terms.table import table
from ieml.ieml_objects.terms.version import DictionaryVersion, get_default_dictionary_version

from ieml.ieml_objects.terms import Term
from ieml.script.constants import MAX_LAYER
from ieml.script.operator import script
from ieml.script.script import AdditiveScript, NullScript, MultiplicativeScript
from ieml import get_configuration, ieml_folder


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


USE_CACHE = get_configuration().get("RELATIONS", "cacherelations")


class Dictionary(metaclass=DictionarySingleton):
    def __init__(self, version, cache=USE_CACHE, load=True):
        super().__init__()

        if isinstance(version, str):
            version = DictionaryVersion(version)

        self.version = version

        self.cache = cache

        # static elements from the version object
        self.terms = None
        self.roots = None
        self.inhibitions = None

        self.index = None

        self.tables = None
        # numpy array
        self.relations = None

        # list layer (int) -> list of terms at this layer
        self._layers = None         # make layers stacks
        self._singular_sequence_map = None

        if load:
            self.load()

    @property
    def is_build(self):
        return all(getattr(self, attr) is not None for attr in ['terms', 'translations', 'roots', 'inhibitions',
                                                                'index', 'ranks', 'partitions', 'parents', 'relations'])

    @property
    def translations(self):
        return self.version.translations

    def load(self):
        cache_folder = os.path.join(
            ieml_folder,
            get_configuration().get("RELATIONS", "cacherelationsfolder"))

        cache_json = os.path.join(cache_folder, 'cache_%s.json'%(str(self.version)))
        cache_relations = os.path.join(cache_folder, 'cache_%s_relations.npy'%(str(self.version)))

        if not os.path.isfile(cache_json) or not os.path.isfile(cache_relations) or not self.cache:
            if not self.is_build:
                self.build()

            if self.cache:
                if not os.path.isdir(cache_folder):
                    os.makedirs(cache_folder)

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
        self._compute_table()
        self._compute_relations()

    @property
    def singular_sequences(self):
        return chain.from_iterable(self.roots)

    @property
    def layers(self):
        if self._layers is None:
            self._layers = [[] for _ in range(MAX_LAYER + 1)]
            for t in self.index:
                self._layers[t.script.layer].append(t)

        return self._layers

    @property
    def _singular_sequences_map(self):
        if self._singular_sequence_map is None:
            self._singular_sequence_map = {ss: r for r in self.roots for ss in r}

        return self._singular_sequence_map

    def __len__(self):
        return len(self.terms)

    def __contains__(self, item):
        return script(item) in self.terms

    def __iter__(self):
        return self.index.__iter__()

    def get_root(self, script):
        try:
            res = {self._singular_sequences_map[self.terms[ss]] for ss in script.singular_sequences}
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

    def _compute_relations(self):
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

        _relations['table'] = self._compute_table_rank(_relations['contained'])
        # for i, t in enumerate(:
        #     _relations['table_%d'%i] = t
        #     _relations['table'] = np.maximum((i + 1.0) * t, _relations['table'])

        missing = {s for s in RELATIONS if s not in _relations}
        if missing:
            raise ValueError("Missing relations : {%s}"%", ".join(missing))

        self.relations = []
        for reltype in RELATIONS:
            self.relations.append(csr_matrix(_relations[reltype]))

    def _compute_table(self):
        print("\t[*] Computing tables")

        self.tables = {}

        for root in self.roots:
            self.tables[root] = table(root, None)
            for t in [t for t in self.roots[root] if len(t) != 1][::-1]:
                self.tables[root].define_paradigm(t)

    def _compute_table_rank(self, contained):
        print("\t\t[*] Computing tables relations")

        _tables_rank = np.zeros((len(self), len(self)))

        for root in self.roots:
            for t0, t1 in combinations(self.roots[root], 2):
                commons = [self.index[i] for i in np.where(contained[t0.index, :] & contained[t1.index, :])[0]]
                _tables_rank[t0.index, t1.index] = max(map(lambda t: t.rank, commons))

        return _tables_rank + _tables_rank.transpose()

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
                   _opposed_sibling(s0.children[0], s1.children[0]) and \
                   _opposed_sibling(s0.children[1], s1.children[1])

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
        }

    def __setstate__(self, state):
        self._populate(relations=state['relations'])

    def _populate(self, relations=None):
        self.version.load()

        all_scripts = [script(s) for s in sorted(self.version.terms, key=len)]

        self.terms = {s: Term(script=s, index=i, dictionary=self) for i, s in enumerate(all_scripts)}
        self.index = [self.terms[s] for s in all_scripts]

        self.inhibitions = {self.terms[r]: v for r, v in self.version.inhibitions.items()}

        # if any(v for v in self.inhibitions.values()):
        #     raise InvalidDictionaryState("")

        self.roots = {self.terms[r]: [] for r in self.version.roots}

        try:
            for t in self.index:
                self.roots[self._singular_sequences_map[t.singular_sequences[0]]].append(t)
        except KeyError as e:
            raise InvalidDictionaryState(self, "No root paradigm for script %s"%str(e.args[0]))

        if relations is not None:
            self.relations = relations

        # reset the cache properties
        self._layers = None
        self._singular_sequences = None

if __name__ == '__main__':

    Dictionary(DictionaryVersion())
