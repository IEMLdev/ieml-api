from itertools import chain

from .commons import IEMLSyntax
from ..exceptions import InvalidIEMLObjectArgument
from .sentences import Sentence, SuperSentence
from .words import Word, Morpheme
from .terms import SyntaxTerm


class Text(IEMLSyntax):
    closable = True

    def __init__(self, children):
        try:
            _children = [e for e in children]
        except TypeError:
            raise InvalidIEMLObjectArgument(Text, "The argument %s is not iterable." % str(children))

        if not all(isinstance(e, (SyntaxTerm, Word, Sentence, SuperSentence, Text)) for e in _children):
            raise InvalidIEMLObjectArgument(Text, "Invalid type instance in the list of a text,"
                                                  " must be Word, Sentence, SuperSentence or Text")

        _children = [Word(Morpheme([c])) if isinstance(c, SyntaxTerm) else c for c in _children]
        _children = list(chain([c for c in _children if not isinstance(c, Text)],
                         *(c.children for c in _children if isinstance(c, Text))))

        super().__init__(sorted(set(_children)))

    def compute_str(self, children_str):
        return '{/' + '//'.join(children_str) + '/}'

    def __contains__(self, item):
        if isinstance(item, Text):
            return all(c in self.children for c in item.children)
        elif isinstance(item,  (Word, Sentence, SuperSentence)):
            return item in self.children

        raise NotImplemented