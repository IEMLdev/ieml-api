from .constants import MAX_SINGULAR_SEQUENCES


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

class InvalidScript(Exception):
    def __str__(self):
        return "Invalid arguments to create a script."


class InvalidScriptCharacter(InvalidScript):
    def __init__(self, character):
        self.character = character

    def __str__(self):
        return 'Invalid character %s for a parser.'%str(self.character)


class TooManySingularSequences(Exception):
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return 'Too many singular sequences in the paradigms (%d, max %d).'%(self.num, MAX_SINGULAR_SEQUENCES)


class IncompatiblesScriptsLayers(InvalidScript):
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2

    def __str__(self):
        return 'Unable to add the two scripts %s, %s they have incompatible layers.'%(str(self.s1), str(self.s2))


class NoRemarkableSiblingForAdditiveScript(Exception):
    pass


class TermNotFoundInDictionary(Exception):
    def __init__(self, term, dictionary):
        self.message = "Cannot find term %s in the dictionary %s" % (str(term), str(dictionary.version))

    def __str__(self):
        return self.message
