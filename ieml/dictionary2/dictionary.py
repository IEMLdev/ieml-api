import hashlib
import pickle

from ieml.constants import LANGUAGES, DICTIONARY_FOLDER
from ieml.dictionary2.script import script
import numpy as np

from collections import namedtuple
import os
import yaml

Translations = namedtuple('Translations', list(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)


def _add_translations(translations, ieml, c):
    translations['fr'][ieml] = c['translations']['fr'].strip()
    translations['en'][ieml] = c['translations']['en'].strip()


class FolderWatcherCache:
    def __init__(self, folder, cache_folder='.'):
        self.folder = folder
        self.cache_folder = cache_folder

    def update(self, obj):
        for c in self._cache_candidates():
            os.remove(c)

        with open(self.cache_file, 'wb') as fp:
            pickle.dump(obj, fp)

    def get(self):
        with open(self.cache_file, 'rb') as fp:
            return pickle.load(fp)

    def is_pruned(self):
        names = self._cache_candidates()
        if len(names) != 1:
            return True

        return self.cache_file != names[0]

    @property
    def cache_file(self):

        hasher = hashlib.md5()
        for file in self._cache_candidates():
            with open(file, 'rb') as fp:
                hasher.update(fp.read())

        return ".dictionary-cache.{}".format(hasher.hexdigest())

    def _cache_candidates(self):
        return [n for n in os.listdir(self.cache_folder) if n.startswith('.dictionary-cache.')]


class Dictionary:

    # def save_cache(self):

    @classmethod
    def load(cls, folder=DICTIONARY_FOLDER, use_cache=True):
        if use_cache:
            cache = FolderWatcherCache(DICTIONARY_FOLDER)
            if not cache.is_pruned():
                return cache.get()

        print("Loading ...")
        scripts = []
        translations = {'fr': {}, 'en': {}}
        roots = []
        inhibitions = {}

        for f in os.listdir(folder):
            with open(os.path.join(folder, f)) as fp:
                d = yaml.load(fp)

            root = d['RootParadigm']['ieml']
            inhibitions[root] = d['RootParadigm']['inhibitions']

            roots.append(root)

            _add_translations(translations, root, d['RootParadigm'])
            scripts.append(root)

            if d['Terms']:
                for c in d['Terms']:
                    scripts.append(c['ieml'])
                    _add_translations(translations, c['ieml'], c)

            if d['Paradigms']:
                for c in d['Paradigms']:
                    scripts.append(c['ieml'])
                    _add_translations(translations, c['ieml'], c)

        dictionary = cls(scripts=scripts, translations=translations, root_paradigms=roots, inhibitions=inhibitions)

        if use_cache:
            cache.update(dictionary)

        return dictionary

    def __init__(self, scripts, root_paradigms, translations, inhibitions):
        print("Parsing ...")
        self.scripts = np.array(sorted(script(s) for s in scripts))

        # list of root paradigms
        self.roots = sum(self.one_hot(r) for r in root_paradigms)

        # scripts to translations
        self.translations = np.array([Translations(fr=translations['fr'][s], en=translations['en'][s]) for s in self.scripts])

        # map of root paradigm script -> inhibitions list values
        self._inhibitions = inhibitions

        # self.tables = TableStructure

    def __len__(self):
        return len(self.scripts)

    def one_hot(self, s):
        return np.array(self.scripts == script(s), dtype=int)


if __name__ == '__main__':
    d = Dictionary.load('/home/louis/code/ieml/ieml-dictionary/dictionary')
    print(len(d))
    print(d.one_hot("e."))
    print(d.roots)
    print(d.scripts)
    d = Dictionary.load('/home/louis/code/ieml/ieml-dictionary/dictionary')
    print(d.scripts)

