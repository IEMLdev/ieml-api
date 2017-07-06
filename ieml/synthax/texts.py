from ..commons import IEMLObjects
from ..exceptions import InvalidIEMLObjectArgument
from .sentences import Sentence, SuperSentence
from .words import Word


class Text(IEMLObjects):
    closable = True

    def __init__(self, children):
        try:
            _children = [e for e in children]
        except TypeError:
            raise InvalidIEMLObjectArgument(Text, "The argument %s is not iterable." % str(children))

        if not all(isinstance(e, (Word, Sentence, SuperSentence)) for e in _children):
            raise InvalidIEMLObjectArgument(Text, "Invalid type instance in the list of a text,"
                                                  " must be Word, Sentence or SuperSentence.")

        super().__init__(sorted(set(_children)))

    def compute_str(self, children_str):
        return '{/' + '//'.join(children_str) + '/}'
