import pickle

from collections import defaultdict

from memory_profiler import profile

from ieml.commons import cached_property
from ieml.dictionary.relations import RelationsGraph
from ieml.dictionary.table import Cell, table_class
from ieml.dictionary.version import save_dictionary_to_cache, load_dictionary_from_cache
from .version import DictionaryVersion, get_default_dictionary_version
from ..constants import MAX_LAYER
from .script import script

from ieml import get_configuration

USE_CACHE = get_configuration().get("RELATIONS", "cacherelations")


class DictionarySingleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], (DictionaryVersion, str)):
            version = get_default_dictionary_version()
        elif isinstance(args[0], DictionaryVersion):
            version = args[0]
        elif isinstance(args[0], str):
            version = DictionaryVersion(args[0])
        else:
            raise ValueError("Invalid argument for dictionary creation, expected dictionary version, not %s"%str(args[0]))

        if cls._instance is None or cls._instance.version != version:
            # check cache
            if not version.is_cached or not USE_CACHE:
                cls._instance = super(DictionarySingleton, cls).__call__(version, **kwargs)

                if USE_CACHE:
                    save_dictionary_to_cache(cls._instance)
            else:
                cls._instance = load_dictionary_from_cache(version)

        return cls._instance


class Dictionary(metaclass=DictionarySingleton):
    def __init__(self, version=None):
        super().__init__()

        if isinstance(version, str):
            version = DictionaryVersion(version)

        self.version = version

        # buildable elements
        self.scripts = None
        self.terms = None
        self.roots = None
        self.inhibitions = None
        self.index = None
        self.relations_graph = None

        self._populate()

        print("\t[*] Dictionary loaded (version: %s, nb_roots: %d, nb_terms: %d)"%
              (str(self.version), len(self.roots), len(self)))

    @cached_property
    def translations(self):
        return self.version.translations

    @cached_property
    def layers(self):
        _layers = [[] for _ in range(MAX_LAYER + 1)]
        for t in self.index:
            _layers[t.script.layer].append(t)

        return _layers

    def __len__(self):
        return len(self.terms)

    def __contains__(self, item):
        return script(item) in self.terms

    def __iter__(self):
        return self.index.__iter__()

    def _define_root(self, root, paradigms, script_index):
        paradigms = sorted(paradigms, key=len, reverse=True)

        self.terms[root] = table_class(root)(root, index=script_index[root], dictionary=self, parent=None)
        defined = {self.terms[root]}

        for ss in root.singular_sequences:
            self.terms[ss] = Cell(script=ss, index=script_index[ss], dictionary=self, parent=self.terms[root])

        for s in paradigms:
            if s in self.terms:
                continue

            candidates = set()
            for t in defined:

                accept, regular = t.accept_script(s)
                if accept:
                    candidates |= {(t, regular)}

            if len(candidates) == 0:
                raise ValueError("No parent candidate for the table produced by term %s" % str(s))

            if len(candidates) > 1:
                print("\t[!] Multiple parent candidate for the table produced by script %s: {%s} "
                      "choosing the smaller one." % (str(s), ', '.join([str(c[0]) for c in candidates])))

            parent, regular = min(candidates, key=lambda t: t[0])

            self.terms[s] = table_class(s)(script=s,
                                           index=script_index[s],
                                           dictionary=self,
                                           parent=parent,
                                           regular=regular)
            defined.add(self.terms[s])

        self.roots[self.terms[root]] = sorted(defined | set(self.terms[root]))

    def _populate(self, scripts=None, relations=None):
        self.version.load()

        if scripts is None:
            self.scripts = sorted(script(s) for s in self.version.terms)
        else:
            self.scripts = scripts

        script_index = {
            s: i for i, s in enumerate(self.scripts)
        }
        roots = defaultdict(list)
        root_ss = {}
        for root in self.version.roots:
            root = script(root)
            for ss in root.singular_sequences:
                root_ss[ss] = root

        for s in self.scripts:
            if s.cardinal == 1:
                continue

            roots[root_ss[s.singular_sequences[0]]].append(s)

        self.terms = {}
        self.roots = {}
        for root in self.version.roots:
            self._define_root(root=script(root), paradigms=roots[root], script_index=script_index)

        self.index = sorted(self.terms.values())
        self.inhibitions = {self.terms[r]: relations_list for r, relations_list in self.version.inhibitions.items()}

        if relations is None:
            self.relations_graph = RelationsGraph(dictionary=self)
        else:
            assert all(rel.shape[0] == len(self) and rel.shape[1] == len(self) for rel in relations)
            self.relations_graph = relations

    def __getstate__(self):
        return {
            'relations': self.relations_graph,
            'scripts': self.scripts,
            'version': str(self.version)
        }

    def __setstate__(self, state):
        if isinstance(state['version'], DictionaryVersion):
            self.version = state['version']
        else:
            self.version = DictionaryVersion(state['version'])
        self._populate(scripts=state['scripts'], relations=state['relations'])
