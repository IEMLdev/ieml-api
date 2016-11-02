import itertools


class IEMLPath:
    def __init__(self, coordinates_sum):
        try:
            self.coordinates_sum = tuple(set(tuple(c) for c in coordinates_sum))
        except TypeError:
            raise ValueError("Can't instantiate an IEMLPath object with %s, must be an iterable of coordinate."
                             %str(coordinates_sum))

        if not self.coordinates_sum:
            self.coordinates_sum = (),

        if any(not isinstance(c, IEMLCoordinate) for sum in self.coordinates_sum for c in sum):
            raise ValueError("Can't instantiate an IEMLPath with non IEMLCoordinate object %s"%str(self.coordinates_sum))

    def __str__(self):
        return '+'.join(':'.join(map(str, sum)) for sum in self.coordinates_sum)

    def __hash__(self):
        return hash(self.coordinates_sum)

    def __eq__(self, other):
        if isinstance(other, IEMLPath):
            return self.coordinates_sum == other.coordinates_sum

    def __add__(self, other):
        if isinstance(other, IEMLPath):
            return IEMLPath(self.coordinates_sum + other.coordinates_sum)

        raise NotImplemented

    # def __mul__(self, other):
    #     if isinstance(other, IEMLPath):
    #         return IEMLPath()
    #
    #     raise NotImplemented

    def __getitem__(self, item):
        return self.coordinates_sum[item]

    def __len__(self):
        return len(self.coordinates_sum)

    @property
    def empty(self):
        return len(self.coordinates_sum) == 1 and not self.coordinates_sum[0]


class IEMLCoordinate(tuple):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, ())

    def _do_add(self, other):
        raise NotImplemented

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self._do_add(other)
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def __hash__(self):
        raise NotImplemented
