import json
from collections import namedtuple, defaultdict

from bidict import bidict

from ieml.commons import LANGUAGES
from ieml.ieml_objects.commons import IEMLObjects
from ieml.script.constants import MAX_LAYER
from ieml.script.operator import script
import os
import yaml
from ieml.script.script import AdditiveScript, NullScript, MultiplicativeScript
from metaclasses import Singleton
import numpy as np

Relations = namedtuple('Relations', ['contains', 'contained', 'father', 'children',
                                     'opposed', 'associated', 'twins', 'crossed'])


class Term(IEMLObjects):
    closable = True

    def __init__(self, s, dictionary):
        self.dictionary = dictionary
        self.script = script(s)

        self.grammatical_class = self.script.script_class

        super().__init__([])

        self._relations = {}

        # if term in a dictionary, those values will be set
        self.translation = None
        self.inhibitions = None
        self.root = None
        # self.rank = None
        self.index = None
        self.relations = None

    # def relations(self, relation_name):
    #     if relation_name not in self._relations:
    #         from models.relations import RelationsQueries
    #         self._relations[relation_name] = \
    #             [Term(s) for s in RelationsQueries.relations(self.script, relation_title=relation_name)]
    #
    #     return self._relations[relation_name]

    __hash__ = IEMLObjects.__hash__

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False

        return self.script == other.script

    def _do_gt(self, other):
        return self.script > other.script

    def compute_str(self, children_str):
        return "[" + str(self.script) + "]"

    @property
    def empty(self):
        return self.script.empty

    @property
    def defined(self):
        return all(self.__getattribute__(p) is not None for p in ['translation', 'inhibitions', 'root', 'index', 'relations'])



def save_dictionary(directory, pickle=True):
    """
    Save the dictionary to a file.
    the roots argument must be the form:
    {
    root_p => {
        paradigms => [{
            paradigm => '',
            translation => {
                fr => '',
                en => ''
            }, ...],
        inhibitions => ['', ...]
        translation => {
                fr => '',
                en => ''
            }
        }
    }
    :param dictionary:
    :param directory:
    :return:
    """

    if pickle:
        # limit = sys.getrecursionlimit()
        # sys.setrecursionlimit(10000)
        file = os.path.join(directory, "dictionary.json")
        relations_file = os.path.join(directory, "dictionary_relations.npy")

        state = Dictionary().__getstate__()
        np.save(arr=state['relations'], file=relations_file)

        del state['relations']

        with open(file, 'w') as fp:
            json.dump(state, fp)

        # sys.setrecursionlimit(limit)
    else:
        def _get_translations(term):
            return {l: Dictionary().translations[l][term] for l in LANGUAGES }

        to_save = [r for r in Dictionary().roots]

        save = {str(root.script): {
            'translation': _get_translations(root),
            'inhibitions': root.inhibitions,
            'paradigms': [{
                'paradigm': str(p.script),
                'translation': _get_translations(p)
            } for p in Dictionary().terms.values() if p.root == root]
        } for root in to_save[:10]}

        file = os.path.join(directory, "dictionary.yml")
        with open(file, 'w') as fp:
            yaml.dump(save, fp)


def load_dictionary(directory, dictionary):
    dic_json = os.path.join(directory, "dictionary.json")
    dic_rel = os.path.join(directory, "dictionary_relations.npy")

    if os.path.isfile(dic_json):
        with open(dic_json, 'r') as fp:
            state = json.load(fp)

        state['relations'] = np.load(dic_rel)
        dictionary.__setstate__(state)
    else:
        file = os.path.join(directory, "dictionary_true.yml")
        print("Loading dictionary ... ", end='', flush=True)

        with open(file, 'r') as fp:
            roots = yaml.load(fp)

        for r_p, v in roots.items():
            dictionary.add_term(r_p, root=True, inhibitions=v['inhibitions'], translation=v['translation'])
            for p in v['paradigms']:
                dictionary.add_term(p['paradigm'], root=False, translation=p['translation'])
        dictionary.compute_relations()
        print("Done.")

        return dictionary


class Dictionary(metaclass=Singleton):
    def __init__(self):

        super().__init__()

        self.terms = {}
        self.translations = {l: bidict() for l in LANGUAGES}
        self.roots = {}
        self.relations = None

        # list layer (int) -> list of terms at this layer
        self._layers = None         # make layers stacks
        self._index = None
        self._singular_sequences = None

        folder = os.path.join(os.path.dirname(__file__), "../../data/dictionary")
        load_dictionary(folder, dictionary=self)

    def __getstate__(self):
        return {
            'index': [str(t.script) for t in self.index],
            'translations': {l: {str(t.script): text for t, text in v.items()} for l, v in self.translations.items()},
            'roots': [str(t.script) for t in self.roots],
            'relations': self.relations
        }

    def __setstate__(self, state):
        self._index = [Term(t, dictionary=self) for t in state['index']]
        assert sorted(self._index) == self._index

        self.terms = {t.script:t for t in self.index}
        self.translations = {l: {self.terms[t]: text for t, text in v.items()} for l, v in state['translations'].items()}
        self.roots = {self.terms[r]: [] for r in state['roots']}
        self.relations = state['relations']

        self._layers = None
        self._singular_sequences = None

        self.define_terms()
        print("loaded !")

    def define_terms(self):
        for i, t in enumerate(self.index):
            t.index = i

        for r, v in self.roots.items():
            for t in v:
                t.root = r

        for t in self.terms.values():
            t.translation = {l: self.translations[l][t] for l in self.translations}
            t.inhibitions = []
            # t.rank = None

        self._set_terms_relations()

    @property
    def singular_sequences(self):
        if self._singular_sequences is None:
            self._singular_sequences = sorted(ss for r in self.roots for ss in r.script.singular_sequences)

        return self._singular_sequences

    @property
    def index(self):
        if self._index is None:
            self._index = sorted(self.terms.values())
        return self._index

    @property
    def layers(self):
        if self._layers is None:
            self._layers = [[] for _ in range(MAX_LAYER + 1)]
            for t in self.index:
                self._layers[t.script.layer].append(t)

        return self._layers

    def add_term(self, script, root=False, inhibitions=(), translation=None):

        term = Term(script, self)

        if term.script in self.terms:
            # print("Term %s already defined."%str(term))
            return

        roots_p = {root_term for root_term in self.roots if term.script in root_term.script}

        if len(roots_p) == 1:
            root_p = next(roots_p.__iter__())

            if root:
                raise ValueError("Root paradigm intersection with term %s when adding root term %s" %
                                 (str(root_p), str(term)))

            self._add_term(term, root_p=root_p, inhibitions=inhibitions, translation=translation)

        elif len(roots_p) > 1:
            raise ValueError("Can't define the term %s in the dictionary, the term is in multiples root paradigms [%s]"%
                             (str(term), ', '.join(map(str, roots_p))))
        elif root:
            if not term.script.paradigm:
                raise ValueError("Can't add the singular sequence term %s as a root paradigm."%str(term))

            self._add_root(term, inhibitions, translation)

        else:
            raise ValueError("Can't add term %s to the dictionary, it is not defined within a root paradigm."%str(term))

    def _add_term(self, term, root_p, inhibitions, translation):
        self.set_translation(term, translation)
        self.roots[root_p].append(term)
        self.terms[term.script] = term

    def _add_root(self, term, inhibitions, translation):
        self.roots[term] = list()
        self._add_term(term, root_p=term, inhibitions=inhibitions, translation=translation)

    def __len__(self):
        return len(self.terms)

    def set_translation(self, term, translation):
        if not isinstance(translation, dict) or len(translation) != 2 or any(not isinstance(v, str) for v in translation.values()):
            raise ValueError("Invalid translation format for term %s."%str(term))

        for l in LANGUAGES:
            if l not in translation:
                raise ValueError("Missing translation for %s language for term %s"%(l, str(term)))

            if translation[l] in self.translations[l].inv:
                raise ValueError("Translation %s provided for term %s already used for term %s."%
                                 (translation[l], str(self.translations[l].inv[translation[l]]), str(term)))

            self.translations[l][term] = translation[l]

    def _compute_contains(self):
        print("Compute contains")
        # contain/contained
        contains = np.diag(np.ones(len(self), dtype=np.int8))
        for r_p, v in self.roots.items():
            paradigms = {t for t in v if t.script.paradigm}

            for p in paradigms:
                _contains = [self.terms[ss].index for ss in p.script.singular_sequences] + \
                           [k.index for k in paradigms if k.script in p.script]
                contains[p.index, _contains] = 1

        contained = contains.transpose()
        return [contains, contained]

    def _compute_father(self):
        print("Compute father/child")
        # father/children
        father = np.zeros((3, len(self), len(self)))
        for t in self.terms.values():
            s = t.script

            for sub_s in s if isinstance(s, AdditiveScript) else [s]:
                if len(sub_s.children) == 0 or isinstance(sub_s, NullScript):
                    continue

                for i in range(3):
                    if isinstance(sub_s.children[i], NullScript):
                        continue

                    if sub_s.children[i] in self.terms:
                        father[i, t.index, self.terms[sub_s.children[i]].index] = 1

        children = np.transpose(father, (0, 2, 1))
        return [father, children]

    def _compute_siblings(self):
        # siblings
        # 1 dim => the sibling type
        #  -0 opposed
        #  -1 associated
        #  -2 twin
        #  -3 crossed

        siblings = np.zeros((4, len(self), len(self)))

        print("Compute siblings")

        _twins = []
        for l in self.layers[1:]:
            for i, t0 in enumerate(l):
                if not isinstance(t0.script, MultiplicativeScript):
                    continue

                if t0.script.children[0] == t0.script.children[1]:
                    _twins.append(t0)

                for t1 in [t for t in l[i:] if isinstance(t.script, MultiplicativeScript)]:

                    def _opposed_sibling(s0, s1):
                        return s0.children[0] == s1.children[1] and s0.children[1] == s1.children[0]

                    def _associated_sibling(s0, s1):
                        return s0.children[0] == s1.children[0] and \
                               s0.children[1] == s1.children[1] and \
                               s0.children[2] != s1.children[2]

                    def _crossed_sibling(s0, s1):
                        return s0.layer > 2 and \
                               _opposed_sibling(s0.children[0], s1.children[1]) and \
                               _opposed_sibling(s0.children[1], s1.children[0])

                    if _opposed_sibling(t0.script, t1.script):
                        siblings[0, t0.index, t1.index] = 1
                        siblings[0, t1.index, t0.index] = 1

                    if _associated_sibling(t0.script, t1.script):
                        siblings[1, t0.index, t1.index] = 1
                        siblings[1, t1.index, t0.index] = 1

                    if _crossed_sibling(t0.script, t1.script):
                        siblings[3, t0.index, t1.index] = 1
                        siblings[3, t1.index, t0.index] = 1

        twin_indexes = [t.index for t in _twins]
        siblings[2, twin_indexes, twin_indexes] = 1

        return siblings

    def _set_terms_relations(self):
        _res = defaultdict(dict)

        for i in range(len(self)):
            t = self.index[i]
            _res[t]['contained'] = [self.index[j] for j in np.where(self.rel('CONTAINED')[i, :] == 1)[0]]
            _res[t]['contains'] = [self.index[j] for j in np.where(self.rel('CONTAINS')[i, :] == 1)[0]]

            _res[t]['father'] = [[], [], []]
            _res[t]['children'] = [[], [], []]
            for k in range(3):
                _res[t]['father'][k] = [self.index[j] for j in
                               np.where(self.relations[RELATION_TYPES_TO_INDEX['FATHER.SUBSTANCE'] + k, i, :] == 1)[0]]
                _res[t]['children'][k] = [self.index[j] for j in
                                 np.where(self.relations[RELATION_TYPES_TO_INDEX['CHILDREN.SUBSTANCE'] + k, i, :] == 1)[0]]

            _res[t]['opposed'] = [self.index[j] for j in np.where(self.rel("OPPOSED")[i, :] == 1)[0]]
            _res[t]['associated'] = [self.index[j] for j in np.where(self.rel("ASSOCIATED")[i, :] == 1)[0]]
            _res[t]['crossed'] = [self.index[j] for j in np.where(self.rel("CROSSED")[i, :] == 1)[0]]
            _res[t]['twins'] = []

        _twins = [self.index[j] for j in np.where(self.rel('TWIN')[:, :] == 1)[0]]
        for t in _twins:
            _res[t]['twins'] = _twins

        for t in _res:
            t.relations = Relations(**_res[t])

    def rel(self, type):
        return self.relations[RELATION_TYPES_TO_INDEX[type], :, :]

    def compute_relations(self):
        for i, t in enumerate(self.index):
            t.index = i

        contains, contained = self._compute_contains()
        father, children = self._compute_father()
        siblings = self._compute_siblings()

        self.relations = np.concatenate((contains[None, :, :],
                                         contained[None, :, :],
                                         father,
                                         children,
                                         siblings), axis=0).astype(np.bool)
        print("Set terms ")
        self._set_terms_relations()


RELATION_TYPES_TO_INDEX = bidict({
    'CONTAINS': 0,
    'CONTAINED': 1,
    'FATHER.SUBSTANCE': 2,
    'FATHER.ATTRIBUTE': 3,
    'FATHER.MODE': 4,
    'CHILDREN.SUBSTANCE': 5,
    'CHILDREN.ATTRIBUTE': 6,
    'CHILDREN.MODE': 7,
    'OPPOSED': 8,
    'ASSOCIATED':9,
    'TWIN': 10,
    'CROSSED': 11
})


if __name__ == '__main__':
    print(os.getcwd())
    d = Dictionary()
    print(len(d))
