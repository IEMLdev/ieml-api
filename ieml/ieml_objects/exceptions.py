

class InvalidIEMLObjectArgument(Exception):
    def __init__(self, type, msg):
        self.type = type
        self.msg = msg

    def __str__(self):
        return 'Invalid arguments to create a %s object. %s'%(str(self.type), str(self.msg))


class TermNotFoundInDictionary(InvalidIEMLObjectArgument):
    def __init__(self, term):
        self.term = term

    def __str__(self):
        return "Cannot find term %s in the dictionnary" % str(self.term)
