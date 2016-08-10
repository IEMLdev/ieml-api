import json


class DBException(Exception):
    def __str__(self):
        return 'Database error.'


class TermAlreadyExists(DBException):
    def __init__(self, script):
        self.script = script

    def __str__(self):
        return 'Term %s already exists in the terms collection.'%str(self.script)


class PropositionAlreadyExists(DBException):
    pass


class TextAlreadyExists(DBException):
    pass


class HypertextAlreadyExists(DBException):
    pass


class ObjectTypeNotStoredinDB(DBException):
    pass


class InvalidTags(DBException):
    def __init__(self, tags):
        self.tags = tags

    def __str__(self):
        return 'The tags are not valid %s, either it is missing a translation or the type is incorrect.'%json.dumps(self.tags)


class DuplicateTag(DBException):
    def __init__(self, tag):
        self.tag = tag

    def __str__(self):
        return 'The tag %s provided is already used in the collection for another element.'%str(self.tag)


class ObjectNotFound(DBException):
    pass


class InvalidASTType(DBException):
    pass


class CollectionAlreadyLocked(DBException):
    def __init__(self, pid, role):
        self.pid = pid
        self.role = role

    def __str__(self):
        return 'Unable to lock the collection, process id:%d has already locked it for role:%s.'%(self.pid, self.role)


class InvalidScript(DBException):
    def __init__(self, script):
        self.script = script

    def __str__(self):
        return 'The script %s provided have not a script compatible type.'%str(self.script)


class NotAParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'The script %s is not a paradigm.'%str(self.p)


class RootParadigmIntersection(DBException):
    def __init__(self, to_add, intersection):
        self.to_add = str(to_add)

        self.intersection = str(intersection)
        if isinstance(self.intersection, (set, list, tuple)):
            self.intersection = str(' '.join(map(str, self.intersection)))

    def __str__(self):
        return 'Singular sequences intersection detected when adding the root paradigm : %s with the following paradigm : %s'%(str(self.to_add), str(self.intersection))


class ParadigmAlreadyExist(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'The paradigm %s already exist in the database.'%str(self.p)


class NotARootParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'Unable to recompute the relations for the following script %s, not a root paradigm.'%str(self.p)


class RootParadigmMissing(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'The root paradigm for the script %s is missing from the db.'%str(self.p)


class SingularSequenceAlreadyExist(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'Unable to save the following singular sequence %s, already present in db.'%str(self.p)


class NotASingularSequence(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return 'Unable to save the following script as a singular sequence, it is a paradigm.'%str(self.p)


class InvalidInhibitArgument(DBException):
    def __init__(self, inhibit):
        self.inhibit = inhibit

    def __str__(self):
        return 'Invalid root paradigm relations inhibition argument, wrong type or unknown keys: %s.'%json.dumps(self.inhibit)


class InvalidMetadata(DBException):
    pass


class CantRemoveNonEmptyRootParadigm(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return "Can't remove the %s non empty root paradigm from the db."%str(self.p)


class InvalidRelationTitle(DBException):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return "The string %s is not a valid relation name."%str(self.p)


class TermNotFound(ObjectNotFound):
    def __init__(self, p):
        self.p = str(p)

    def __str__(self):
        return "The term %s is not present in db."%str(self.p)


class InvalidRelationCollectionState(DBException):
    def __str__(self):
        return 'The relation collection is in an invalid state, the cause is often the adding of some term without calculating the relations. Please recompute the collection.'