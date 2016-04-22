
class DBException(Exception):
    pass


class PropositionAlreadyExists(DBException):
    pass


class ObjectTypeNotStoredinDB(DBException):
    pass