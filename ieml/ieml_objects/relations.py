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
             'siblings'          # 16
             ]


class Relations:
    def __init__(self, term, dictionary):
        super().__init__()

        self.dictionary = dictionary
        self.term = term
        self.clear()

    def clear(self):
        self._contains = None
        self._contained = None

        self._father_substance = None
        self._child_substance = None

        self._father_attribute = None
        self._child_attribute = None
        self._father_mode = None
        self._child_mode = None

        self._siblings_crossed = None
        self._siblings_associated = None
        self._siblings_opposed = None
        self._siblings_twin = None

        self._inclusion = None
        # self._etymology = [
        #     sorted(set(self._father_substance + self._child_substance)),
        #     sorted(set(self._father_attribute + self._child_attribute)),
        #     sorted(set(self._father_mode + self._child_mode))
        # ]

        self._father = None
        self._children = None
        self._siblings = None
        self._all = None
        self._all_tuple = None

        self._table_0 = None
        self._table_1 = None
        self._table_2 = None
        self._table_3 = None
        self._table_4 = None
        self._table_5 = None

        self._all_table = None
        self._root = None
        self._all_relations = None

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

    def to(self, term, table=False):
        if table:
            if self._all_table is None:
                self._all_table = defaultdict(list)
                for relname in ["table_%d"%i for i in range(6)]:
                    for t in self[relname]:
                        self._all_table[t].append(relname)

            return self._all_table[term]
        else:
            if self._all_relations is None:
                self._all_relations = defaultdict(list)
                for relname in ['opposed', 'associated', 'crossed', 'twin', 'root']:
                    for t in self[relname]:
                        self._all_relations[t].append(relname)

            return self._all_relations[term]


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

    def _rels(self, s):
        return tuple(self.dictionary.rel(s, self.term))

    def inclusion(self):
        return self._contains + self._contained

    @property
    def contains(self):
        if self._contains is None:
            self._contains = self._rels("contains")

        return self._contains

    @property
    def contained(self):
        if self._contained is None:
            self._contained = self._rels("contained")

        return self._contained

    @property
    def father_substance(self):
        if self._father_substance is None:
            self._father_substance = self._rels("father_substance")

        return self._father_substance

    @property
    def father_attribute(self):
        if self._father_attribute is None:
            self._father_attribute = self._rels("father_attribute")

        return self._father_attribute

    @property
    def father_mode(self):
        if self._father_mode is None:
            self._father_mode = self._rels("father_mode")

        return self._father_mode

    @property
    def child_substance(self):
        if self._child_substance is None:
            self._child_substance = self._rels("child_substance")

        return self._child_substance

    @property
    def child_attribute(self):
        if self._child_attribute is None:
            self._child_attribute = self._rels("child_attribute")

        return self._child_attribute

    @property
    def child_mode(self):
        if self._child_mode is None:
            self._child_mode = self._rels("child_mode")

        return self._child_mode

    @property
    def father(self):
        if self._father is None:
            self._father = sorted(set(self.father_substance + self.father_attribute + self.father_mode))
        return self._father

    @property
    def child(self):
        if self._child is None:
            self._child = sorted(set(self.child_substance + self.child_attribute + self.child_mode))

        return self._child

    @property
    def crossed(self):
        if self._siblings_crossed is None:
            self._siblings_crossed = self._rels("crossed")

        return self._siblings_crossed

    @property
    def associated(self):
        if self._siblings_associated is None:
            self._siblings_associated = self._rels("associated")

        return self._siblings_associated

    @property
    def opposed(self):
        if self._siblings_opposed is None:
            self._siblings_opposed = self._rels("opposed")

        return self._siblings_opposed


    @property
    def root(self):
        if self._root is None:
            self._root = self.term.root.relations.contains
        return self._root


    @property
    def twin(self):
        if self._siblings_twin is None:
            self._siblings_twin = self._rels("twin")

        return self._siblings_twin

    @property
    def siblings(self):
        if self._siblings is None:
            self._siblings = tuple(sorted(set(self.associated + self.crossed + self.opposed + self.twin)))
        return self._siblings

    @property
    def table_0(self):
        if self._table_0 is None:
            self._table_0 = self._build_relations_table(0)
        return self._table_0

    @property
    def table_1(self):
        if self._table_1 is None:
            self._table_1 = self._build_relations_table(1)
        return self._table_1

    @property
    def table_2(self):
        if self._table_2 is None:
            self._table_2 = self._build_relations_table(2)
        return self._table_2

    @property
    def table_3(self):
        if self._table_3 is None:
            self._table_3 = self._build_relations_table(3)

        return self._table_3

    @property
    def table_4(self):
        if self._table_4 is None:
            self._table_4 = self._build_relations_table(4)
        return self._table_4

    @property
    def table_5(self):
        if self._table_5 is None:
            self._table_5 = self._build_relations_table(5)
        return self._table_5


    def _build_relations_table(self, lvl):
        return tuple(sorted(set(t for p in self.term.root.relations.contains if self.term in p and p.rank == lvl
                                    for t in p.relations.contains if not t.script.paradigm)))