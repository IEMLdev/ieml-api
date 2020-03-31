from ieml.commons import DecoratedComponent
from ieml.dictionary.script import Script


class USL(DecoratedComponent):
    syntactic_level = 0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singular_sequences = None
        self._singular_sequences_set = None
        self._str = None

        self.grammatical_class = None

    def __bool__(self):
        return not self.empty

    @property
    def empty(self):
        raise NotImplementedError()

    def check(self):
        raise NotImplementedError()

    def __str__(self):
        return self._str
    
    def __lt__(self, other):
        if isinstance(other, Script):
            return False

        from ieml.usl.decoration.instance import InstancedUSL
        if isinstance(other, InstancedUSL):
            other = other.usl

        return self.syntactic_level < other.syntactic_level or \
               (self.syntactic_level == other.syntactic_level and self.do_lt(other))

    def do_lt(self, other):
        raise NotImplementedError()

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        """Since the IEML string for a script is its definition, it can be used as a hash"""
        return self._str.__hash__()

    def __len__(self):
        return self.cardinal

    def __contains__(self, item):
        return item.singular_sequences_set.issubset(self.singular_sequences_set)

    def iter_structure(self):
        raise NotImplementedError()

    def iter_structure_path(self, flexion=False):
        raise NotImplementedError()


    @property
    def cardinal(self):
        return len(self.singular_sequences)

    @property
    def singular_sequences(self):
        if self._singular_sequences is None:
            self._singular_sequences = self._compute_singular_sequences()

        return self._singular_sequences

    @property
    def singular_sequences_set(self):
        if self._singular_sequences_set is None:
            self._singular_sequences_set = set(self.singular_sequences)

        return self._singular_sequences_set

    def _compute_singular_sequences(self):
        raise NotImplementedError

    @property
    def is_singular(self):
        return self.cardinal == 1

    @property
    def morphemes(self):
        raise NotImplementedError()


def usl(arg):
    if isinstance(arg, str):
        from ieml.usl.parser import IEMLParser
        return IEMLParser().parse(arg)

    if isinstance(arg, Script):
        from ieml.usl import PolyMorpheme
        return PolyMorpheme([arg])

    if isinstance(arg, USL):
        return arg

    from ieml.lexicon.paths import resolve_ieml_object, path
    if isinstance(arg, dict):
        # map path -> Ieml_object
        return resolve_ieml_object(arg)

    # if iterable, can be a list of usl to convert into a text
    try:
        usl_list = list(arg)
    except TypeError:
        pass
    else:
        if len(usl_list) == 0:
            return usl('E:')

        if all(isinstance(u, USL) for u in usl_list):
            if len(usl_list) == 1:
                return usl_list[0]
            else:
                from ieml.lexicon import text
                return text(usl_list)
        else:
            # list of path objects
            try:
                rules = [(a, b) for a, b in usl_list]
            except TypeError:
                pass
            else:
                rules = [(path(a), usl(b)) for a, b in rules]
                return resolve_ieml_object(rules)

    raise NotImplementedError()
