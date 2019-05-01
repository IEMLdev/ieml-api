import ast
from itertools import chain
import pandas as pd
from collections import defaultdict

from ieml.constants import INHIBITABLE_RELATIONS
from ieml.dictionary.script import Script, script
from typing import List, Dict

from ieml.ieml_database.descriptor import monitor_decorator

LEVELS_CLASSES = ['trait', 'character', 'word']


class LexiconStructure:
    """
    index : ['paradigm', 'level']
    columns : ['singular_sequences']
    """

    def __init__(self, structure):
        self.structure = structure.set_index(['paradigm', 'level'], verify_integrity=True)

    # def from_description(self, paradigms):
    #     for p in paradigms:


    @staticmethod
    def from_file(file):
        with open(file) as fp:
            return LexiconStructure(pd.read_csv(fp, sep=' ', converters={'singular_sequences': ast.literal_eval}))
    def write_to_file(self, file):
        with open(file, 'w') as fp:
            self.structure.reset_index().to_csv(fp, sep=' ', index=False)

    def get(self, paradigm, level):
        assert level in LEVELS_CLASSES
        try:
            return list(self.structure.loc(axis=0)[(str(paradigm), level)])
        except KeyError:
            return []

    def add_singular_sequence(self, paradigm, level, singular_sequences):
        assert level in LEVELS_CLASSES
        self.structure.loc(axis=0)[(paradigm, level)] = sorted(set(self.get(paradigm, level)) | {singular_sequences})