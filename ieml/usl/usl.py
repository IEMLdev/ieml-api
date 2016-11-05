from ieml.paths.paths import Path
from ieml.paths.tools import enumerate_paths, resolve


class Usl:
    def __init__(self, ieml_object):
        self.ieml_object = ieml_object
        self._rules = None

    def __str__(self):
        return str(self.ieml_object)

    def __eq__(self, other):
        if isinstance(other, Usl):
            return self.ieml_object.__eq__(other.ieml_object)

    def __hash__(self):
        return hash(self.ieml_object)

    @property
    def paths(self):
        if self._rules is None:
            self._rules = tuple(enumerate_paths(self.ieml_object))

        return self._rules

    def __getitem__(self, item):
        if isinstance(item, Path):
            return resolve(self.ieml_object, item)

        raise NotImplemented