from collections import OrderedDict, defaultdict

NB_RELATIONS = 12

RELATIONS = ['contains',         # 0
             'contained',        # 1
             'father_substance', # 2
             'child_substance',  # 3
             'father_attribute', # 4
             'child_attribute',  # 5
             'father_mode',      # 6
             'child_mode',       # 7
             'opposed',          # 8
             'associated',       # 9
             'crossed',          # 10
             'twin',             # 11

             'table_0',
             'table_1',
             'table_2',
             'table_3',
             'table_4',
             'table_5',

             'inclusion',        # 12
             'father',           # 13
             'child',            # 14
             'etymology',        # 15
             'siblings',         # 16
             'table'             # 17
             ]

INVERSE_RELATIONS = {
    'father_substance': 'child_substance',
    'child_substance': 'father_substance',  # 3
    'father_attribute': 'child_attribute', # 4
    'child_attribute': 'father_attribute',  # 5
    'father_mode': 'child_mode',      # 6
    'child_mode': 'father_mode',
    'contains': 'contained',
    'contained': 'contains',
    'opposed':'opposed',          # 8
    'associated':'associated',       # 9
    'crossed': 'crossed',        # 10
    'twin': 'twin',
    'table_0': 'table_0',
    'table_1': 'table_1',
    'table_2': 'table_2',
    'table_3': 'table_3',
    'table_4': 'table_4',
    'table_5': 'table_5',
    'father': 'child',
    'child': 'father',
    'inclusion': 'inclusion',
    'etymology': 'etymology',        # 15
    'siblings': 'siblings',         # 16
    'table': 'table'
}


class Relations:
    def __init__(self, term, dictionary):
        super().__init__()

        self.dictionary = dictionary
        self.term = term
        self._all = None
        for reltype in RELATIONS:
            setattr(self, "_%s" % reltype, None)

    def all(self, dict=False):
        if self._all is None:
            rels = defaultdict(list)

            for reltype in RELATIONS:
                for t in self[reltype]:
                    rels[t].append(reltype)

            self._all = OrderedDict()

            for t in sorted(rels):
                self._all[t] = rels[t]

            self._all_tuple = tuple(self._all)

        if dict:
            return self._all
        else:
            return self._all_tuple

    def to(self, term, relations_types=None):
        if relations_types is None:
            relations_types = RELATIONS

        if term not in self.all(dict=True):
            return []

        relations = self.all(dict=True)[term]
        result = []
        for reltype in relations:
            if reltype in relations_types:
                result.append(reltype)

        return result

    def __iter__(self):
        return self.all().__iter__()

    def __len__(self):
        return len(self.all())

    def __contains__(self, item):
        return item in self.all(dict=True)

    def __getitem__(self, item):
        if isinstance(item, int):
            item = RELATIONS[item]

        if isinstance(item, str):
            return self.__getattribute__(item)

        raise NotImplemented


def get_relation(reltype):
    def getter(self):
        if getattr(self, "_%s" % reltype) is None:
            relations = tuple(self.dictionary.rel(reltype, term=self.term))
            setattr(self, "_%s" % reltype, relations)

        return getattr(self, "_%s" % reltype)

    return getter

for reltype in RELATIONS:
    setattr(Relations, reltype, property(fget=get_relation(reltype)))


if __name__ == '__main__':
    from ieml.ieml_objects.tools import term
    t = term("wa.")
    print([str(tt) for tt in t.relations.etymology])