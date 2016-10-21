class IEMLPath:
    def __init__(self, coordinates):
        try:
            self.coordinates = tuple(coordinates)
        except TypeError:
            raise ValueError("Can't instantiate an IEMLPath object with %s, must be an iterable of coordinate."
                             %str(coordinates))

    def __str__(self):
        return ':'.join(map(str, self.coordinates))

    def __hash__(self):
        return hash(self.coordinates)

    def __eq__(self, other):
        if isinstance(other, IEMLPath):
            return self.coordinates == other.coordinates

    def __add__(self, other):
        if isinstance(other, IEMLPath):
            if len(self.coordinates) != other.coordinates:
                raise ValueError("Can't add two paths with different length %d, %d."%
                                 (len(self.coordinates), len(other.coordinates)))
            return IEMLPath([s + o for s, o in zip(self.coordinates, other.coordinates)])

        raise NotImplemented

    def __mul__(self, other):
        if isinstance(other, IEMLPath):
            return IEMLPath(self.coordinates + other.coordinates)

        raise NotImplemented

    def __getitem__(self, item):
        return self.coordinates[item]

    def __len__(self):
        return len(self.coordinates)