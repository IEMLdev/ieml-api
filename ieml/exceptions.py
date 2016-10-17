

class InvalidPathException(Exception):
    def __init__(self, tree_elem, path):
        self.tree_elem = tree_elem
        self.path = path

    def __str__(self):
        return "Can't access %s in %s children, the path is invalid : %s"%(str(self.path[0]), str(self.tree_elem),
                                                                           str(self.path))


class ParserErrors(Exception):
    pass


class CannotParse(ParserErrors):
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return "Unable to parse the following string %s."%str(self.s)