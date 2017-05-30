from collections import OrderedDict, defaultdict
from functools import partial

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
             'siblings'          # 16
             ]


class Relations:
    def __init__(self, term, dictionary):
        super().__init__()

        self.dictionary = dictionary
        self.term = term

        def get_relation(reltype):
            def getter(self):
                if getattr(self, "_%s" % reltype) is None:
                    relations = tuple(self.dictionary.rel(reltype, term=self.term))
                    setattr(self, "_%s" % reltype, relations)

                return getattr(self, "_%s" % reltype)

            return getter

        for reltype in RELATIONS:
            setattr(self, "_%s"%reltype, None)
            setattr(self.__class__, reltype, property(fget=get_relation(reltype)))

    def all(self, dict=False):
        if self._all is None:
            rels = defaultdict(list)

            for i in range(NB_RELATIONS):
                relname = RELATIONS[i]
                for t in self[i]:
                    rels[t].append(relname)

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

        result = []
        for reltype in relations_types:
            if term in getattr(self, reltype):
                result.append(reltype)

        return result





        # if table:
        #     if self._all_table is None:
        #         self._all_table = defaultdict(list)
        #         for relname in ["table_%d"%i for i in range(6)]:
        #             for t in self[relname]:
        #                 self._all_table[t].append(relname)
        #
        #     return self._all_table[term]
        # else:
        #     if self._all_relations is None:
        #         self._all_relations = defaultdict(list)
        #         for relname in ['opposed', 'associated', 'crossed', 'twin', 'root']:
        #             for t in self[relname]:
        #                 self._all_relations[t].append(relname)
        #
        #     return self._all_relations[term]

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


if __name__ == '__main__':
    from ieml.ieml_objects.tools import term
    t = term("wa.")
    print([str(tt) for tt in t.relations.etymology])