import hashlib
import dill

import sys

from ieml.constants import LANGUAGES, DICTIONARY_FOLDER
from ieml.dictionary.relation.relations import RelationsGraph
from ieml.dictionary.script import script
import numpy as np

from collections import namedtuple
import os
import yaml

from ieml.dictionary.table.table_structure import TableStructure

Translations = namedtuple('Translations', list(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)

class FolderWatcherCache:
    def __init__(self, folder, cache_folder):
        self.folder = folder
        self.cache_folder = os.path.abspath(cache_folder)

    def update(self, obj):
        for c in self._cache_candidates():
            os.remove(c)

        with open(self.cache_file, 'wb') as fp:
            dill.dump(obj, fp)

    def get(self):
        with open(self.cache_file, 'rb') as fp:
            return dill.load(fp)

    def is_pruned(self):
        names = [p for p in self._cache_candidates()]
        if len(names) != 1:
            return True

        return self.cache_file != names[0]

    @property
    def cache_file(self):
        res = b""
        for file in sorted(os.listdir(self.folder)):
            with open(os.path.join(self.folder, file), 'rb') as fp:
                res += file.encode('utf8') + b":" + fp.read()

        return os.path.join(self.cache_folder, ".dictionary-cache.{}".format(hashlib.md5(res).hexdigest()))

    def _cache_candidates(self):
        return [os.path.join(self.cache_folder, n) for n in os.listdir(self.cache_folder) if n.startswith('.dictionary-cache.')]


class Dictionary:
    @classmethod
    def load(cls, folder=DICTIONARY_FOLDER, use_cache=True, cache_folder=os.path.abspath('.')):
        print("Dictionary.load: Reading dictionary at {}".format(folder), file=sys.stderr)

        if use_cache:
            cache = FolderWatcherCache(folder, cache_folder=cache_folder)
            if not cache.is_pruned():
                print("Dictionary.load: Reading cache at {}".format(cache.cache_file), file=sys.stderr)

                return cache.get()

            print("Dictionary.load: Dictionary files changed  Recomputing cache.", file=sys.stderr)

        scripts = []
        translations = {'fr': {}, 'en': {}}

        def _add_translations(ieml, c):
            translations['fr'][ieml] = c['translations']['fr'].strip()
            translations['en'][ieml] = c['translations']['en'].strip()

        roots = []
        inhibitions = {}

        n_ss = 0
        n_p = 0
        for f in os.listdir(folder):
            with open(os.path.join(folder, f)) as fp:
                d = yaml.load(fp)

            root = d['RootParadigm']['ieml']
            inhibitions[root] = d['RootParadigm']['inhibitions']

            roots.append(root)

            _add_translations(root, d['RootParadigm'])
            scripts.append(root)

            if 'Semes' in d and d['Semes']:
                for c in d['Semes']:
                    n_ss += 1
                    scripts.append(c['ieml'])
                    _add_translations(c['ieml'], c)

            if 'Paradigms' in d and d['Paradigms']:
                for c in d['Paradigms']:
                    n_p += 1
                    scripts.append(c['ieml'])
                    _add_translations(c['ieml'], c)

        print("Dictionary.load: Read {} root paradigms, {} paradigms and {} semes".format(len(roots), n_p, n_ss), file=sys.stderr)

        print("Dictionary.load: Computing table structure and relations ...", file=sys.stderr)
        dictionary = cls(scripts=scripts, translations=translations, root_paradigms=roots, inhibitions=inhibitions)
        print("Dictionary.load: Computing table structure and relations", file=sys.stderr)

        if use_cache:
            print("Dictionary.load: Updating cache at {}".format(cache.cache_file), file=sys.stderr)
            cache.update(dictionary)

        return dictionary

    def __init__(self, scripts, root_paradigms, translations, inhibitions):
        self.scripts = np.array(sorted(script(s) for s in scripts))
        self.index = {e: i for i, e in enumerate(self.scripts)}

        # list of root paradigms
        self.roots_idx = sum(self.one_hot(r) for r in root_paradigms)

        # scripts to translations
        self.translations = {s: Translations(fr=translations['fr'][s], en=translations['en'][s]) for s in self.scripts}

        # map of root paradigm script -> inhibitions list values
        self._inhibitions = inhibitions

        # self.tables = TableStructure
        self.tables = TableStructure(self.scripts, self.roots_idx)

        self.relations = RelationsGraph(dictionary=self)

    def __len__(self):
        return self.scripts.__len__()

    def one_hot(self, s):
        return np.eye(len(self))[self.index[s]]


    def __getitem__(self, item):
        return self.scripts[self.index[script(item)]]

    def __contains__(self, item):
        return item in self.index


if __name__ == '__main__':
    d = Dictionary.load('/home/louis/code/ieml/ieml-dictionary/dictionary')
    rel = d.relations.pandas()
    print(set(rel[rel['mode'] == 'father_attribute']['attribute']))