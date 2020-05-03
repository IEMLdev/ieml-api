from typing import Iterable, Tuple, Union, List, Set

from ieml.commons import DecoratedComponent
from ieml.dictionary.script import Script
# from ieml.usl.decoration.path import UslPath


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

    def iter_structure(self, auto_promote_to_USL=False):
        raise NotImplementedError()

    def iter_structure_path(self, flexion=False) -> Iterable[Tuple['UslPath', 'USL']]:
        raise NotImplementedError()

    def iter_structure_path_by_type(self, _type=Script, flexion=False,):
        for path, item in self.iter_structure_path(flexion=flexion):
            if isinstance(item, _type):
                yield (path, item)

    def iter_structure_path_by_script_ss(self, flexion=False) -> Iterable[Tuple['UslPath', Script]]:
        from ieml.usl.decoration.path import PolymorphemePath
        from ieml.usl.decoration.path import FlexionPath

        for path, item in self.iter_structure_path(flexion=flexion):
            if isinstance(path.tail, (FlexionPath, PolymorphemePath)) and path.tail.morpheme is not None:
                yield (path, item)

    @property
    def cardinal(self) -> int:
        return len(self.singular_sequences)

    @property
    def singular_sequences(self) -> List['USL']:
        if self._singular_sequences is None:
            self._singular_sequences = self._compute_singular_sequences()

        return self._singular_sequences

    @property
    def singular_sequences_set(self) -> Set['USL']:
        if self._singular_sequences_set is None:
            self._singular_sequences_set = set(self.singular_sequences)

        return self._singular_sequences_set

    def _compute_singular_sequences(self):
        raise NotImplementedError()

    @property
    def is_singular(self) -> bool:
        return self.cardinal == 1

    @property
    def morphemes(self) -> Set[Script]:
        raise NotImplementedError()


def usl(arg: Union[str, Script, USL, Iterable[Tuple['UslPath', Union[USL, Script]]]]) -> USL:
    """

    Cast argument to an USL type, depending on the argument type.
     - If argument is a string, it is parsed by ieml.usl.parser.IEMLParser.parse
     - if argument is a ieml.dictionary.Script, the returned object is a
       ieml.usl.polymorpheme.PolyMorpheme with the argument as the constant.
     - if argument is an ieml.usl.usl.USL, the argument is returned
     - if argument is a list of (ieml.usl.decoration.path.UslPath, ieml.usl.usl.USL)

    :param arg:
    :type arg: Union[str, Script, USL, Iterable[Tuple['UslPath', Union[USL, Script]]]]
    :return: an ieml.usl.usl.USL
    """
    if isinstance(arg, str):
        from ieml.usl.parser import IEMLParser
        return IEMLParser().parse(arg)

    if isinstance(arg, Script):
        from ieml.usl import PolyMorpheme
        return PolyMorpheme(constant=[arg])

    if isinstance(arg, USL):
        return arg


    #if iterable, can be a list of (path, usl) to convert into an usl
    try:
        usl_list = list(arg)
    except TypeError:
        pass
    else:
        if not usl_list:
            from ieml.usl import PolyMorpheme
            return PolyMorpheme(constant=[])

        from ieml.usl.decoration.path import UslPath, usl_from_path_values

        if not all(isinstance(u, (USL, Script)) and isinstance(p, UslPath) for p, u in usl_list):
            raise ValueError("Invalid iterable of (UslPath, USL) to create an USL from.")

        return usl_from_path_values(usl_list)

    # from ieml.lexicon.paths import resolve_ieml_object, path
    # if isinstance(arg, dict):
    #     # map path -> Ieml_object
    #     return resolve_ieml_object(arg)

    # if iterable, can be a list of usl to convert into a text
    # try:
    #     usl_list = list(arg)
    # except TypeError:
    #     pass
    # else:
    #     if len(usl_list) == 0:
    #         return usl('E:')
    #
    #     if all(isinstance(u, USL) for u in usl_list):
    #         if len(usl_list) == 1:
    #             return usl_list[0]
    #         else:
    #             from ieml.lexicon import text
    #             return text(usl_list)
    #     else:
    #         # list of path objects
    #         try:
    #             rules = [(a, b) for a, b in usl_list]
    #         except TypeError:
    #             pass
    #         else:
    #             rules = [(path(a), usl(b)) for a, b in rules]
    #             return resolve_ieml_object(rules)

    raise NotImplementedError()
