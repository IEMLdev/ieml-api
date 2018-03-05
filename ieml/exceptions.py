from .constants import MAX_SINGULAR_SEQUENCES


class InvalidPathException(Exception):
    def __init__(self, element, path, message):
        self.element = element
        self.path = path
        self.message = message

    def __str__(self):
        return "Can't access %s in %s, %s."%(str(self.path), str(self.element), str(self.message))


class CannotParse(Exception):
    def __init__(self, s, msg):
        self.s = s
        self.msg = msg

    def __str__(self):
        return "Unable to parse the following string '%s'. %s"%(str(self.s), str(self.msg))


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
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return "Invalid arguments to create a script. "+ self.msg if self.msg else ""


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


class TermNotFoundInDictionary(Exception):
    def __init__(self, term, dictionary):
        self.message = 'Cannot find term "{0}" in the dictionary {1}'.format(str(term), str(dictionary.version))

    def __str__(self):
        return self.message


class ScriptNotDefinedInVersion(Exception):
    def __init__(self, script, version):
        self.message = "Script {1} not defined in the dictionary version {1}".format(str(script), str(version))

    def __str__(self):
        return self.message

class PathError(Exception):
    def __init__(self, message, path):
        self.message = message
        self.path = path

    def __str__(self):
        return self.message + "[%s]" % str(self.path)

class ResolveError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

class IEMLObjectResolutionError(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "Invalid ieml object definitions at:\n%s" % (
            '\n'.join("\t[%s] %s" % (str(p), e) for p, e in self.errors))