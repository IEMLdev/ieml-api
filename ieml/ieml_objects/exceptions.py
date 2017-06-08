

class InvalidIEMLObjectArgument(Exception):
    def __init__(self, type, msg):
        self.type = type
        self.message = msg

    def __str__(self):
        return 'Invalid arguments to create a %s object. %s'%(self.type.__name__, str(self.message))


class InvalidTreeStructure(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return 'Invalid tree structure. %s'%str(self.message)

class CantGenerateElement(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return 'Unable to generate element. %s'%self.message