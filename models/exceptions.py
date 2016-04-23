
class DBException(Exception):
    pass


class PropositionAlreadyExists(DBException):
    pass


class ObjectTypeNotStoredinDB(DBException):
    pass

class InvalidTags(DBException):
    pass

class ObjectNotFound(DBException):
    pass