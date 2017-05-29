

class InvalidPathException(Exception):
    def __init__(self, element, path):
        self.element = element
        self.path = path

    def __str__(self):
        return "Can't access %s in %s, the path is invalid."%(str(self.path), str(self.element))


class CannotParse(Exception):
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return "Unable to parse the following string %s."%str(self.s)