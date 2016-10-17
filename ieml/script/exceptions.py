from ieml.script.constants import MAX_SINGULAR_SEQUENCES


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