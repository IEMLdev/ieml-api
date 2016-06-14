class DBException(Exception):
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


class ObjectNotFound(DBException):
    pass


class InvalidASTType(DBException):
    pass


class InvalidScript(DBException):
    pass


class NotAParadigm(DBException):
    pass


class InvalidDbState(DBException):
    pass


class RootParadigmIntersection(DBException):
    pass


class ParadigmAlreadyExist(DBException):
    pass


class NotARootParadigm(DBException):
    pass



class RootParadigmMissing(DBException):
    pass
