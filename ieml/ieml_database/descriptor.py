import ast
import operator

import pandas as pd

from collections import namedtuple, defaultdict, OrderedDict
import os, re

from functools import reduce

from ieml.constants import LANGUAGES
from ieml.dictionary.script import Script, script as sc
from itertools import product

DESCRIPTORS_CLASS=['comments', 'translations']


def set_value(self, key, value):
    if key in LANGUAGES:
        self.__setattribute__(key, value)
    else:
        raise ValueError('Invalid argument {} {}'.format(key, value))

Translations = namedtuple('Translations', sorted(LANGUAGES))
Translations.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)

Comments = namedtuple('Comments', sorted(LANGUAGES))
Comments.__getitem__ = lambda self, item: self.__getattribute__(item) if item in LANGUAGES \
    else tuple.__getitem__(self, item)

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


class DescriptorSet:
    # file = ['descriptors/{}/{}'.format(l, k) for l, k in product(LANGUAGES, DESCRIPTORS_CLASS)]

    file = ['descriptors/dictionary']

    def __init__(self, descriptors):
        # if descriptors.duplicated(['script', 'language', 'descriptor']).any():
        #     raise ValueError("Duplicated entries")
        # descriptors.index.name = 'index'
        #
        self.descriptors = descriptors.set_index(['script', 'language', 'descriptor'], verify_integrity=True, drop=True)

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
        for k in set(map(lambda e: sc(e, factorize=True), keys)):
            for l in LANGUAGES:
                for desc in DESCRIPTORS_CLASS:
                    v = kwargs[desc].get(l, {k: []}).get(k, [])
                    index.append([str(k), l, desc, v])

        dt = pd.DataFrame(index, columns=['script', 'language', 'descriptor', 'values'])
        return DescriptorSet(dt)

    @monitor_decorator('write_to_folder')
    def write_to_folder(self, db_folder):
        for l in LANGUAGES:
            path_l = os.path.join(db_folder, 'descriptors', l)
            if not os.path.isdir(path_l):
                os.mkdir(path_l)

            for k in DESCRIPTORS_CLASS:
                f_path = os.path.join(db_folder, 'descriptors', l, k)
                with open(f_path, 'w') as fp:
                    for sc in sorted(self.descriptors):
                        trans = self.descriptors[sc][l][k]
                        _str = ' '.join('"{}"'.format(re.sub('"', '""', t)) for t in trans)
                        _str = _str.encode("unicode_escape").decode('utf8')

                        fp.write("{} {}\n".format(str(sc), _str))

    @monitor_decorator('write_to_file')
    def write_to_file(self, file):
        with open(file, 'w') as fp:
            return self.descriptors.reset_index().to_csv(fp, sep=' ', index=False)

    @staticmethod
    @monitor_decorator('from_file')
    def from_file(file):
        with open(file, 'r') as fp:
            return DescriptorSet(pd.read_csv(fp, sep=' ', converters={'values': ast.literal_eval}))

    def set_value(self, script, language, descriptor, values):
        assert sc(script, factorize=True) == script, "Script not factorized {} : {}".format(str(script), str(sc(script, factorize=True)))
        assert descriptor in DESCRIPTORS_CLASS
        assert language in LANGUAGES
        assert isinstance(values, list) and all(isinstance(v, str) for v in values)

        self.descriptors.loc[(str(script), language, descriptor)] = [values]

    def __len__(self):
        return len(self.descriptors)

    def __iter__(self):
        return iter(self.descriptors)

    # def __getitem__(self, item):
    #     return self.descriptors.__getitem__(item)
        # if isinstance(item, Script):
        #     try:
        #         return self.descriptors[item]
        #     except KeyError:
        #         self.descriptors[item] = Descriptor()
        #         return self.descriptors[item]
        # else:
        #     raise KeyError(item)

    def get(self, script=None, language=None, descriptor=None):
        # kwargs = {'script':script, 'language': language, 'descriptor': descriptor}

        key = (str(script), language, descriptor)

        if all(v is not None for v in key):
            try:
                return list(self.descriptors.loc(axis=0)[key])[0]
            except KeyError:
                return []
        else:
            key = {'script': str(script), 'language': language, 'descriptor': descriptor}
            key = reduce(operator.and_,  [self.descriptors.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                         True)
            return self.descriptors[key].to_dict()['values']
    #
    # @staticmethod
    # @monitor_decorator('from_folder')
    # def from_folder(db_folder):
    #     descriptors = {k: {ll: defaultdict(list) for ll in LANGUAGES} for k in DESCRIPTORS_CLASS}
    #     for l in LANGUAGES:
    #         for k in DESCRIPTORS_CLASS:
    #
    #             f_path = os.path.join(db_folder, 'descriptors', l, k)
    #
    #             with open(f_path) as fp:
    #                 for line in fp:
    #                     try:
    #                         sc, trans = line.strip().split(' ', 1)
    #                     except ValueError:
    #                         continue
    #                     for t in re.findall(r'("(?:""|[^"])+")', trans):
    #                         t = t.encode('utf-8').decode('unicode-escape')
    #                         t = re.sub(r'""', '"', t[1:-1])
    #
    #                         descriptors[k][l][sc].append(t)
    #
    #     return DescriptorSet.build_descriptors(**descriptors)


class Descriptor:
    def __init__(self, translations=None, comments=None):

        if not translations:
            translations = {l:[] for l in LANGUAGES}

        if not comments:
            comments = {l:[] for l in LANGUAGES}

        self.default = Translations(**{l: translations[l][0] if len(translations[l]) else '' for l in LANGUAGES})
        self.translations = translations
        self.comments = comments

    def default(self):
        return self.default

    # def __setitem__(self, key, value):
    #     if isinstance(value, dict):
    #         if key in DESCRIPTORS_CLASS:
    #             assert isinstance(value, dict) and all(k in LANGUAGES for k in value)
    #         elif key in LANGUAGES:
    #             assert isinstance(value, dict) and all(k in DESCRIPTORS_CLASS for k in value)
    #         else:
    #             raise ValueError("Invalid arguments {} {}".format(key, value))
    #
    #         for k in value:
    #             super().__getattribute__(key)[k] = value[k]
    #
    #     raise ValueError("Invalid arguments {} {}".format(key, value))

    def set_translations(self, translations):
        assert isinstance(translations, dict) and all(l in translations for l in LANGUAGES)
        self.translations = translations

    def __getitem__(self, item):
        if item in LANGUAGES:
            return {'default': self.default,
                    'translations': self.translations[item] if self.translations[item] else ['???'],
                    'comments': self.comments[item]}
        elif item in DESCRIPTORS_CLASS:
            return {
                l: self[l][item] for l in LANGUAGES
            }
        else:
            raise KeyError(item)

if __name__ == '__main__':
    # DescriptorSet.from_folder = monitor_decorator("classic")(DescriptorSet.from_folder)
    folder = '/home/louis/.cache/ieml/1.0.3/e116865545e9e8132dd87e6d62d01040'
    ds = DescriptorSet._from_folder(folder)

    file_desc = os.path.join(folder, 'descriptors/dictionary')
    ds.write_to_folder(file_desc)
    ds2 = DescriptorSet.from_folder(file_desc)
    print(ds2.descriptors[ds2['descriptor'] == 'translations'])
    # assert ds.descriptors.equals(ds2.descriptors)


    @monitor_decorator('dt_from_ds')
    def dt_from_ds(ds):
        SER = []
        for s in ds:
            for l in LANGUAGES:
                for k in DESCRIPTORS_CLASS:
                    SER.append({'language': l, 'script': str(s), 'descriptor': k, 'values': ds[s].get(k, {l: []}).get(l, [])})
        return pd.DataFrame(SER)


    STRATEGIES = ['to_pickle', 'to_parquet', 'to_csv']#, 'to_feather']#, 'to_hdf']

    dt = dt_from_ds(ds)
    def write_folder_pandas(dt, file, strat):
        # with open(file, 'w') as fp:
        getattr(dt, strat)(file)

    import pickle

    @monitor_decorator('write_pickle_pd')
    def write_pickle_pd(file, dt):
        with open(file, 'wb') as fp:
            return dt.to_pickle(fp)


    @monitor_decorator('read_pickle_pd')
    def read_pickle_pd(file):
        with open(file, 'rb') as fp:
            return pickle.load(fp)


    file = "{}/{}".format(folder, 'pickle')

    write_pickle_pd(file, dt)
    read_pickle_pd(file)

    # def get_io_strat(strat):
    #     @monitor_decorator(strat)
    #     def read(file):
    #         pd.
    #
    # def read_folder_pandas(dt, file, strat):
    #     # with open(file, 'w') as fp:
    #     getattr(dt, strat)(file)
    #
    # f_stratw = [lambda e: monitor_decorator(s)(write_folder_pandas(e, "{}/{}".format(folder, s) , s)) for s in STRATEGIES]
    # f_stratr = [lambda e: monitor_decorator(s)(write_folder_pandas(e, "{}/{}".format(folder, s) , s)) for s in STRATEGIES]
    #
    # for f in f_strat:
    #     f(dt)

