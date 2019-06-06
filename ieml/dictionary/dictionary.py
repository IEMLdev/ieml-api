from collections import defaultdict

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

class Dictionary2:
    def __init__(self, paradigms, structure):
        scripts = {s: script(s, factorize=True) for s in paradigms}

        root_paradigms = []
        inhibitions = defaultdict(list)
        ignored = []
        for (root, key), (value,) in structure.df.iterrows():
            root = scripts[root]

            for ss in root.singular_sequences:
                scripts[str(ss)] = ss


            if key == 'inhibition':
                inhibitions[root].append(value)
            elif key == 'is_root' and value[0].lower() == 't':
                root_paradigms.append(root)
            elif key == 'is_ignored' and value[0].lower() == 't':
                ignored.append(root)

        for s in ignored:
            root_paradigms.remove(s)
            if str(s) in scripts:
                del scripts[s]
            if s in inhibitions:
                del inhibitions[s]

        # map of root paradigm script -> inhibitions list values
        self._inhibitions = inhibitions

        self.scripts = np.array(sorted(scripts.values()))

        self.tables = TableStructure(self.scripts, root_paradigms)

        self.scripts = np.array([s for s in self.scripts if len(s) == 1 or s in self.tables.tables])
        self.index = {e: i for i, e in enumerate(self.scripts)}

        self.roots_idx = np.zeros((len(self.scripts),), dtype=int)
        self.roots_idx[[self.index[r] for r in root_paradigms]] = 1

        self.relations = RelationsGraph(dictionary=self)

    def __len__(self):
        return self.scripts.__len__()

    def __getitem__(self, item):
        return self.scripts[self.index[script(item)]]

    def __contains__(self, item):
        return item in self.index