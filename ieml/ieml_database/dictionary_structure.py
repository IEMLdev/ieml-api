import ast
from itertools import chain
import pandas as pd
from collections import defaultdict

from ieml.constants import INHIBITABLE_RELATIONS
from ieml.dictionary.script import Script, script
from typing import List, Dict
import re, os

from ieml.ieml_database.descriptor import monitor_decorator


def _check_inhibitions(inhibitions):
    assert all(all(rel in INHIBITABLE_RELATIONS for rel in i) for i in inhibitions.values()), \
        "Invalid inhibitions"

def _check_paradigm(r, pl):
    assert all(isinstance(p, Script) and script(p, factorize=True) == p for p in pl)
    assert isinstance(r, Script) and script(r, factorize=True) == r and len(r) != 1
    assert all(p in r for p in pl)

def _check_roots(roots):
    all_ss = list(chain.from_iterable(r.singular_sequences) for r in roots)
    assert len(set(all_ss)) == len(all_ss), "Root intersections: {}".format(' '.join(map(str, roots)))

class DictionaryStructure:
    file = ['structure/dictionary']

    def __init__(self, structure):
        self.structure = structure.set_index(['root'], verify_integrity=True)

    @staticmethod
    def from_structure(scripts: List[Script], roots: List[Script], inhibitions: Dict[Script, List[str]]):
        _check_inhibitions(inhibitions)
        _check_roots(roots)
        root_to_paradigms = defaultdict(list)

        for s in scripts:
            if s.cardinal == 1 or s in roots:
                # ignore ss and roots
                continue

            for r in roots:
                if s in r:
                    root_to_paradigms[r].append(str(s))
                    break
            else:
                raise ValueError("Paradigm in no root paradigms {}".format(str(s)))

        _inhibitions = defaultdict(list)
        _inhibitions.update(inhibitions)

        df = pd.DataFrame(data=[[str(r), root_to_paradigms[r], _inhibitions[r]] for r in root_to_paradigms],
                          columns=['root', 'paradigms', 'inhibitions'])
        return DictionaryStructure(df)

    @staticmethod
    def from_dictionary(dictionary):
        return DictionaryStructure.from_structure(scripts=dictionary.scripts,
                                                  roots=list(dictionary.tables.roots),
                                                  inhibitions=dictionary._inhibitions)

    @staticmethod
    @monitor_decorator("Dictionary description from_file")
    def from_file(file):
        with open(file) as fp:
            return DictionaryStructure(pd.read_csv(fp, sep=' ', converters={'paradigms': ast.literal_eval,
                                                                            'inhibitions': ast.literal_eval}))

    def write_to_file(self, file):
        with open(file, 'w') as fp:
            self.structure.reset_index().to_csv(fp, sep=' ', index=False)
            # fp.write(repr(self))

    def get(self, root=None):
        return list(self.structure.loc[str(root)])

    def set_value(self, root, paradigms, inhibitions):
        paradigms = [script(p) for p in paradigms]
        _check_paradigm(script(root), paradigms)
        _check_inhibitions({'':inhibitions})
        _check_roots([script(r) for r in set(self.structure.index.values) | {root}])

        self.structure.loc(axis=0)[str(root)] = [list(map(str, paradigms)), inhibitions]
