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
    file = ['descriptors/dictionary']

    def __init__(self, descriptors):
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

