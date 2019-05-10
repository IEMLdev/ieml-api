import ast
import operator

import pandas as pd

from collections import namedtuple, defaultdict, OrderedDict
import os, re

from functools import reduce

from ieml.constants import LANGUAGES
from ieml.dictionary.script import Script
from ieml.ieml_database.lexicon.lexicon_structure import LEVELS_CLASSES
from ieml.lexicon.grammar.parser2 import IEMLParser
from ieml.lexicon.grammar.parser2.lexer import TERM_REGEX
from ieml.lexicon.syntax import MorphemeSerie, Trait, Character, Word, LexicalItem

DESCRIPTORS_CLASS=['comments', 'translations']


# def set_value(self, key, value):
#     if key in LANGUAGES:
#         self.__setattribute__(key, value)
#     else:
#         raise ValueError('Invalid argument {} {}'.format(key, value))

# Translations = namedtuple('Translations', sorted(LANGUAGES))
# Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
#     else tuple.__getitem__(self, item)
#
# Comments = namedtuple('Comments', sorted(LANGUAGES))
# Comments.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
#     else tuple.__getitem__(self, item)


from time import time

def monitor_decorator(name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            before = time()
            res = f(*args, **kwargs)
            print(name, time() - before)
            return res

        # functools.wraps(wrapper)
        return wrapper

    return decorator


# PREFIX_LEVEL={'': 'morpheme',
#               '': 'morpheme_serie',
#               '': 'trait'}

def get_level_from_ieml(ieml):
    ieml = str(ieml)
    if ieml.startswith('['):
        return 'character'
    elif ieml.startswith('('):
        return 'word'
    elif ieml.startswith('<'):
        return 'trait'
    elif ' ' in ieml:
        return 'morpheme_serie'
    else:
        assert re.fullmatch(TERM_REGEX, ieml)
        return 'morpheme'

def get_key(obj):
    if isinstance(obj, str):
        obj = IEMLParser().parse(obj)

    if isinstance(obj, Script):
        return str(obj), 'morpheme'

    elif obj.empty:
        return 'E:', 'morpheme'

    elif isinstance(obj, MorphemeSerie):
        if not obj.groups and len(obj.constant) == 1:
            return get_key(obj.constant[0])
        else:
            return str(obj), 'morpheme_serie'
    elif isinstance(obj, Trait):
        if not obj.periphery:
            return get_key(obj.core)
        else:
            return str(obj), 'trait'
    elif isinstance(obj, Character):
        if not obj.functions:
            return get_key(obj.content)
        else:
            return str(obj), 'character'
    elif isinstance(obj, Word):
        if obj.attribute.empty and obj.mode.empty:
            return get_key(obj.substance)
        else:
            return str(obj), 'word'


class LexiconDescriptorSet:
    """

        index :
        ["ieml", "level", "language", "descriptor"] => ['values']

        desc.set(ieml_obj, lang, descriptor, values)
        desc.get(ieml_obj)


        save to file
        split by:
            - language
            - descriptor

        descriptors(df)
        desc.write_to_folder()
        > descriptors:
            > fr
                > morpheme
                > morpheme_serie
                > trait
                > character
                > word

    """

    sub_folder = 'descriptors'
    LEVELS = ['morpheme', 'morpheme_serie', 'trait', 'character', 'word']

    def __init__(self, descriptors=None):
        if descriptors is None:
            descriptors= pd.DataFrame(columns=['ieml', 'language', 'descriptor', 'values'])

        self.descriptors = descriptors.set_index(['ieml', 'language', 'descriptor'], verify_integrity=True, drop=True)

    def is_defined(self, ieml):
        key, _ = get_key(ieml)
        return key in self.descriptors.index.get_level_values('ieml')

    @staticmethod
    def build_descriptors(**kwargs):
        assert all(d in kwargs for d in DESCRIPTORS_CLASS)

        keys = set()
        for l in LANGUAGES:
            for d in DESCRIPTORS_CLASS:
                try:
                    keys = keys.union(map(str, kwargs[d][l]))
                except KeyError:
                    pass

        index = []
        for k in set(keys):
            for l in LANGUAGES:
                for desc in DESCRIPTORS_CLASS:
                    v = kwargs[desc].get(l, {k: []}).get(k, [])
                    index.append([str(k), l, desc, v])

        dt = pd.DataFrame(index, columns=['ieml', 'language', 'descriptor', 'values'])
        return LexiconDescriptorSet(dt)

    def get_files(self):
        return [os.path.join(self.sub_folder, l, level) for l in LANGUAGES for level in LEVELS_CLASSES]

    @monitor_decorator('write_to_file')
    def write_to_file(self, file):
        with open(file, 'w') as fp:
            return self.descriptors.reset_index().to_csv(fp, sep=' ', index=False)

    @monitor_decorator('write_to_folder')
    def write_to_folder(self, folder):
        df = self.descriptors.reset_index()
        for l in df['language'].unique():
            f_l = os.path.join(folder, self.sub_folder, l)
            if not os.path.isdir(f_l):
                os.mkdir(f_l)

            levels = self.descriptors.index.get_level_values('ieml').map(get_level_from_ieml)

            for level in self.LEVELS:
                file = os.path.join(f_l, level)

                df_ser = df[(levels == level) & (df.language == l)]
                df_ser = df_ser.drop(['language'], axis=1)

                with open(file, 'w') as fp:
                    df_ser.to_csv(fp, sep=' ', index=False)

    @staticmethod
    @monitor_decorator('read_from_folder')
    def from_folder(folder):
        f_l = os.path.join(folder, LexiconDescriptorSet.sub_folder)
        res = []
        for l in os.listdir(f_l):
            for level in LexiconDescriptorSet.LEVELS:
                file = os.path.join(f_l, l, level)
                with open(file) as fp:
                    df = pd.read_csv(fp, sep=' ', converters={'values': ast.literal_eval})

                df['language'] = l
                res.append(df)

        return LexiconDescriptorSet(pd.concat(res))

    @staticmethod
    @monitor_decorator('from_file')
    def from_file(file):
        with open(file, 'r') as fp:
            return LexiconDescriptorSet(pd.read_csv(fp, sep=' ', converters={'values': ast.literal_eval}))

    def set_value(self, ieml, language, descriptor, values):
        # assert sc(script, factorize=True) == script, "Script not factorized {} : {}".format(str(script), str(sc(script, factorize=True)))
        # IEMLParser().parse(ieml)
        assert descriptor in DESCRIPTORS_CLASS
        assert language in LANGUAGES
        assert isinstance(values, list) and all(isinstance(v, str) for v in values)

        key, _ = get_key(ieml)

        self.descriptors.loc[(key, language, descriptor)] = [values]

    def __len__(self):
        return len(self.descriptors)

    def __iter__(self):
        return iter(self.descriptors)

    def __contains__(self, item):
        return self.is_defined(item)

    def get(self, ieml=None, language=None, descriptor=None):
        # kwargs = {'script':script, 'language': language, 'descriptor': descriptor}

        if ieml is not None:
            ieml, level = get_key(ieml)

        key = (ieml, language, descriptor)

        if all(v is not None for v in key):
            try:
                return list(self.descriptors.loc(axis=0)[key])[0]
            except KeyError:
                return []
        else:
            key = {'ieml': ieml, 'language': language, 'descriptor': descriptor}
            key = reduce(operator.and_,  [self.descriptors.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                         True)
            return self.descriptors[key].to_dict()['values']

    # def get(self, ieml_obj, l):
    #
    #
    #     # kwargs = {'script':script, 'language': language, 'descriptor': descriptor}
    #
    #     if ieml is not None:
    #         ieml = str(ieml)
    #     key = (ieml, language, descriptor)
    #
    #     if all(v is not None for v in key):
    #         try:
    #             return list(self.descriptors.loc(axis=0)[key])[0]
    #         except KeyError:
    #             return []
    #     else:
    #         key = {'ieml': ieml, 'language': language, 'descriptor': descriptor}
    #         key = reduce(operator.and_,  [self.descriptors.index.get_level_values(k) == v for k, v in key.items() if v is not None],
    #                      True)
    #         return self.descriptors[key].to_dict()['values']


# if __name__ == '__main__':
#     LexiconDescriptorSet.from_file('')