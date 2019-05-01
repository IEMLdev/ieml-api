from ieml.dictionary.relation.relations import RelationsGraph
from ieml.dictionary.script import script
import numpy as np

from ieml.dictionary.table.table_structure import TableStructure
from ieml.ieml_database.dictionary_structure import DictionaryStructure


class Dictionary:
    def __init__(self, dictionary_structure: DictionaryStructure):
        scripts = []
        root_paradigms = []
        inhibitions = {}

        for root, (paradigms, _inhibitions) in dictionary_structure.structure.iterrows():
            root = script(root, factorize=True)
            root_paradigms.append(root)
            scripts.append(root)

            scripts.extend(root.singular_sequences)

            paras = [script(p, factorize=True) for p in paradigms]
            scripts.extend(paras)

            inhibitions[root] = _inhibitions

        self.scripts = np.array(sorted(scripts))
        self.index = {e: i for i, e in enumerate(self.scripts)}

        self.roots_idx = np.zeros((len(self.scripts),), dtype=int)
        self.roots_idx[[self.index[r] for r in root_paradigms]] = 1

        # map of root paradigm script -> inhibitions list values
        self._inhibitions = inhibitions

        # self.tables = TableStructure
        self.tables = TableStructure(self.scripts, self.roots_idx)

        self.relations = RelationsGraph(dictionary=self)

    def __len__(self):
        return self.scripts.__len__()

    def __getitem__(self, item):
        return self.scripts[self.index[script(item)]]

    def __contains__(self, item):
        return item in self.index
