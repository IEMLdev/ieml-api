from itertools import groupby




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


class IEMLCoordinate:
    def __init__(self, rank, elements):
        """

        :param rank:
        :param elements: (type, instanciation|None)
        """
        if not isinstance(rank, int):
            raise ValueError('Not a valid rank %s.'%str(rank))

        self.rank = rank

        try:
            self.elements = sorted(((e[0], e[1]) for e in elements), key=lambda e: e[0])
        except Exception:
            raise ValueError("Must be an iterable.")

        if any(not isinstance(e[0], str) or not isinstance(e[1], int) for e in self.elements):
            raise ValueError("Not valid coordinates.")

        self.elements = {t: instances if None not in instances else None
                         for t, instances in groupby(self.elements, key=lambda e: e[0])}

        self.values = tuple((t, v) for t in sorted(self.elements)
                            for v in (sorted(self.elements[t]) if self.elements[t] else (None,)))

    def __add__(self, other):
        if isinstance(other, self.__class__):
            if self.rank != other.rank:
                raise ValueError("Can't add two coordinates of differents ranks.")

            return IEMLCoordinate(self.rank, self.values + other.values)

        raise NotImplemented

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.rank == other.rank and self.values == other.values

        raise NotImplemented

    def __hash__(self):
        return hash(self.values)

    # def __contains__(self, item):
    #     if isinstance(item, IEMLCoordinate):
    #         return all(v[0] in self.elements and
    #                    (isinstance(self.elements[v[0]], NoneType) or v[1] in self.elements[v[0]])
    #                    for v in item.values)
    #
    #     raise NotImplemented

    def __str__(self):
        if len(self.values) > 1:
            return '(' + '+'.join(str(v[0]) + (str(v[1]) if v[1] else '') for v in self.values)
        v = self.values[0]
        return str(v[0]) + (str(v[1]) if v[1] else '')

    def __mul__(self, other):
        if isinstance(other, IEMLCoordinate):
            return IEMLPath([self, other])

        raise NotImplemented