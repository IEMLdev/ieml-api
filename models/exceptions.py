class DBException(Exception):
    pass


class TermAlreadyExists(DBException):
    pass


class PropositionAlreadyExists(DBException):
    pass


class TextAlreadyExists(DBException):
    pass


class HypertextAlreadyExists(DBException):
    pass


class ObjectTypeNotStoredinDB(DBException):
    pass


class InvalidTags(DBException):
    pass


class DuplicateTag(DBException):
    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return self.tag


class ObjectNotFound(DBException):
    pass


class InvalidASTType(DBException):
    pass


class InvalidScript(DBException):
    pass


class NotAParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class InvalidDbState(DBException):
    pass


class RootParadigmIntersection(DBException):
    def __init__(self, p1, p2):
        self.p1 = str(p1)
        self.p2 = str(p2)

    def __str__(self):
        return '%s, %s'%(self.p1, self.p2)


class ParadigmAlreadyExist(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class NotARootParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class RootParadigmMissing(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class SingularSequenceAlreadyExist(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class NotASingularSequence(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class InvalidInhibitArgument(DBException):
    pass


class InvalidMetadata(DBException):
    pass


class CantRemoveNonEmptyRootParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class InvalidRelationTitle(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p


class TermNotFound(ObjectNotFound):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return self.p

