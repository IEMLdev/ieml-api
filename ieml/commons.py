

class cached_property:
    def __init__(self, factory):
        self._factory = factory
        self._attr_name = factory.__name__

    def __get__(self, instance, owner):
        attr = self._factory(instance)
        setattr(instance, self._attr_name, attr)
        return attr


class TreeStructure:
    def __init__(self):
        self._str = None
        self._paths = None
        self.children = None
        super().__init__()

    def __str__(self):
        return self._str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not isinstance(other, (TreeStructure, str)):
            return False

        return self._str == str(other)

    def __hash__(self):
        """Since the IEML string for any proposition AST is supposed to be unique, it can be used as a hash"""
        return self.__str__().__hash__()

    def __iter__(self):
        """Enables the syntactic sugar of iterating directly on an element without accessing "children" """
        return self.children.__iter__()

    def tree_iter(self):
        yield self
        for c in self.children:
            yield from c.tree_iter()


def fullname(cls):
    return cls.__module__ + '.' + cls.__qualname__


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # this code is to clean up duplicate class if we reload modules
            to_remove = [i for i in cls._instances if fullname(i) == fullname(cls)]
            for i in to_remove:
                del cls._instances[i]

            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]