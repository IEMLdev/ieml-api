
import sys
from bidict import bidict

from ieml.commons import LANGUAGES
from ieml.ieml_objects.commons import IEMLObjects
from ieml.script.constants import MAX_LAYER
from ieml.script.operator import script
import os
import yaml
import pickle as pkl
from ieml.script.script import AdditiveScript, NullScript, MultiplicativeScript
from metaclasses import Singleton
import numpy as np


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
        self.rank = None
        self.index = None

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
        return all(self.__getattribute__(p) is not None for p in ['translation', 'inhibitions', 'root', 'rank', 'index'])



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
        limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        file = os.path.join(directory, "dictionary.pkl")
        with open(file, 'wb') as fp:
            pkl.dump(Dictionary(), fp)
        sys.setrecursionlimit(limit)
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
    file_name = "dictionary"
    dic_pkl = os.path.join(directory, os.path.join(directory, file_name, ".pkl"))
    if os.path.isfile(dic_pkl):
        with open(dic_pkl, 'r') as fp:
            Singleton._instances[Dictionary] = pkl.load(fp)
            return Singleton._instances[Dictionary]
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

        self.singular_sequences = set()
        self.terms = {}
        self.translations = {l: bidict() for l in LANGUAGES}
        self.roots = {}
        self.index = []

        # list layer (int) -> list of terms at this layer
        self._layers = None         # make layers stacks
        self.relations = None

        folder = os.path.join(os.path.dirname(__file__), "../../data/dictionary")
        d = load_dictionary(folder, dictionary=self)
        if d != self:
            print("New dictionary instancied")

    def __getstate__(self):
        return {
            'index': [str(t) for t in self.index],
            'translations': {l: {str(t.script): text for t, text in v.items()} for l, v in self.translations.items()},
            'roots': [str(t.script) for t in self.roots],
            'relations': self.relations
        }

    def __setstate__(self, state):
        self.index = [Term(t, dictionary=self) for t in state['index']]
        self.terms = {t.script:t for t in self.index}
        self.translations = {l: {self.terms[t]: text for t, text in v.items()} for l, v in state['translations'].items()}
        self.roots = {self.terms[r]: [] for r in state['roots']}
        self.relations = state['relations']

    @property
    def layers(self):
        if self._layers is None:
            for t in self.terms
            self._layers = [[] for _ in range(MAX_LAYER + 1)]


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

            self._define_term(term, root_p=root_p, inhibitions=inhibitions, translation=translation)

        elif len(roots_p) > 1:
            raise ValueError("Can't define the term %s in the dictionary, the term is in multiples root paradigms [%s]"%
                             (str(term), ', '.join(map(str, roots_p))))
        elif root:
            if not term.script.paradigm:
                raise ValueError("Can't add the singular sequence term %s as a root paradigm."%str(term))

            self._define_root(term, inhibitions, translation)

        else:
            raise ValueError("Can't add term %s to the dictionary, it is not defined within a root paradigm."%str(term))

    def _define_term(self, term, root_p, inhibitions, translation):

        self.set_translation(term, translation)

        term.root = root_p
        self.roots[root_p].append(term)

        term.inhibitions = inhibitions

        self.layer_stack[term.script.layer].append(term)

        self.terms[term.script] = term

    def _define_root(self, term, inhibitions, translation):
        self.roots[term] = list()
        self.singular_sequences |= set(term.script.singular_sequences)

        self._define_term(term, root_p=term, inhibitions=inhibitions, translation=translation)

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

        term.translation = translation

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
        for l in self.layer_stack[1:]:
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
        _twins = [self.index[j] for j in np.where(self.siblings[2, :, :] == 1)[0]]
        for t in _twins:
            t.twins = _twins

        for i in range(len(self)):
            t = self.index[i]
            t.contained = [self.index[j] for j in np.where(self.contained[i, :] == 1)[0]]
            t.contains = [self.index[j] for j in np.where(self.contains[i, :] == 1)[0]]

            t.father = [[], [], []]
            t.children = [[], [], []]
            for k in range(3):
                t.father[k] = [self.index[j] for j in np.where(self.father[k, i, :] == 1)[0]]
                t.children[k] = [self.index[j] for j in np.where(self.children[k, i, :] == 1)[0]]

            t.opposed = [self.index[j] for j in np.where(self.siblings[0, i, :] == 1)[0]]
            t.associated = [self.index[j] for j in np.where(self.siblings[1, i, :] == 1)[0]]
            t.crossed = [self.index[j] for j in np.where(self.siblings[2, i, :] == 1)[0]]

    def compute_relations(self):
        self.index = sorted(self.terms.values())
        for i, t in enumerate(self.index):
            t.index = i

        contains, contained = self._compute_contains()
        father, children = self._compute_father()
        siblings = self._compute_siblings()

        self.relations = np.concatenate((contains[None, :, :],
                                         contained[None, :, :],
                                         father,
                                         children,
                                         siblings), axis=0)
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
    save_dictionary('../../data/dictionary')
    print(d.father)
    print(len(d))
