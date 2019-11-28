from collections import defaultdict

from tqdm import tqdm

from ieml.dictionary.relation.relations import RelationsGraph
from ieml.dictionary.script import script
import numpy as np

from ieml.dictionary.table.table_structure import TableStructure


class Dictionary:
    def __init__(self, paradigms, structure):
        scripts = {s: script(s, factorize=False) for s in tqdm(paradigms)}

        root_paradigms = []
        inhibitions = defaultdict(list)
        ignored = []
        for (p, key), (value,) in structure.df.iterrows():
            if p not in scripts:
                # print(p)
                continue
            p = scripts[p]

            for ss in p.singular_sequences:
                scripts[str(ss)] = ss


            if key == 'inhibition':
                inhibitions[p].append(value)
            elif key == 'is_root' and value[0].lower() == 't':
                root_paradigms.append(p)
            elif key == 'is_ignored' and value[0].lower() == 't':
                ignored.append(p)

        # ignore all scripts that are not in a root paradigm
        singular_sequences = set()
        for r in root_paradigms:
            if any(ss in singular_sequences for ss in r.singular_sequences):
                raise ValueError("Root paradigms overlap with {}".format(str(r)))
            singular_sequences |= r.singular_sequences_set

        for s in scripts.values():
            if not s.singular_sequences_set.issubset(singular_sequences):
                ignored.append(s)

        for s in ignored:
            del scripts[str(s)]
            if s in root_paradigms:
                root_paradigms.remove(s)
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

    # def __new__(cls, *args, **kwargs):
    #     """
    #     Need this to pickle scripts, the pickler use __hash__ method before unpickling the
    #     object attribute. Then need to pass the _str.
    #     """
    #     instance = super(Dictionary2, cls).__new__(cls)
    #
    #     return instance
    #
    # def __getnewargs_ex__(self):
    #     return ((), {
    #         'str': str(self)
    #     })




    def __len__(self):
        return self.scripts.__len__()

    def __getitem__(self, item):
        return self.scripts[self.index[script(item)]]

    def __contains__(self, item):
        return item in self.index