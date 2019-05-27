import ast
from itertools import chain
import pandas as pd
from collections import defaultdict
import os
from ieml.constants import INHIBITABLE_RELATIONS
from ieml.dictionary.script import Script, script
from typing import List, Dict

from ieml.ieml_database.descriptor import monitor_decorator

LEVELS_CLASSES = ['morpheme', 'poly_morpheme', 'word']


class LexiconStructure:
    """
    index : ['paradigm', 'domain']
    columns:
    """

    def __init__(self, structure=None):
        if structure is None:
            structure = pd.DataFrame(columns=['paradigm', 'domain'])

        self.structure = structure.set_index(['paradigm'], verify_integrity=True)

    def __iter__(self):
        return self.structure.iterrows()

    @staticmethod
    def from_folder(folder, domains):

        res = []
        for d in domains:
            file = os.path.join(folder, d)

            with open(file) as fp:
                df = pd.read_csv(fp, sep=' ')#, converters={'singular_sequences': ast.literal_eval}))

            df['domain'] = d
            res.append(df)
        return LexiconStructure(pd.concat(res))

    @property
    def domains(self):
        return sorted(self.structure['domain'].unique())

    def write_to_folder(self, folder):
        for d in self.domains:
            file = os.path.join(folder, d)

            df_noidx = self.structure.reset_index()
            sub_df = df_noidx[df_noidx.domain == d]

            with open(file, 'w') as fp:
                sub_df.to_csv(fp, sep=' ', index=False)

    def get(self, paradigm):
        # assert level in LEVELS_CLASSES
        try:
            return list(self.structure.loc(axis=0)[(str(paradigm))])
        except KeyError:
            return []


    # def add_paradigm(self, paradigm, domain):
    #     assert self.get()

    def add_paradigm(self, paradigm, domain):
        # paradigms = [script(p) for p in paradigms]
        # _check_paradigm(script(root), paradigms)
        # _check_inhibitions({'':inhibitions})
        # _check_roots([script(r) for r in set(self.structure.index.values) | {root}])

        self.structure.loc(axis=0)[str(paradigm)] = domain

    # def add_singular_sequence(self, paradigm, level, singular_sequences):
    #     assert level in LEVELS_CLASSES
    #     self.structure.loc(axis=0)[(paradigm, level)] = sorted(set(self.get(paradigm, level)) | {singular_sequences})