from ieml.ieml_objects.commons import IEMLObjects
from ieml.ieml_objects.exceptions import InvalidIEMLObjectArgument


class AbstractClause(IEMLObjects):
    def __init__(self, subtype, substance=None, attribute=None, mode=None, children=None):
        super().__init__()

        if not (substance or children):
            raise ValueError()

        if children is None:
            children = [substance, attribute, mode]
            if any(e is None for e in children):
                raise InvalidIEMLObjectArgument(self.__class__, "Must specify a substance, an attribute and a mode.")

        if not all(isinstance(e, subtype) for e in children):
            raise InvalidIEMLObjectArgument(self.__class__, "The children of a %s must be a %s instance."%
                                            (str(self.__class__), str(subtype)))

        if children[0] == children[1]:
            raise InvalidIEMLObjectArgument(self.__class__, "The attribute and the substance (%s) must be distinct."%
                                            (str(children[0])))

        self.children = tuple(children)

    @property
    def substance(self):
        return self.children[0]

    @property
    def attribute(self):
        return self.children[1]

    @property
    def mode(self):
        return self.children[2]

    @property
    def grammatical_class(self):
        return self.attribute.grammatical_class


def AbstractSentence(IEMLObjects):
    def __init__(self, subtype, clause_list):
        super().__init__()

        try:
            _children = tuple(e for e in clause_list)
        except TypeError:
            raise InvalidIEMLObjectArgument(self.__class__, "The argument %s is not an iterable" % str(clause_list))


