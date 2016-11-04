from _operator import mul
from collections import namedtuple, defaultdict
from itertools import groupby, chain, product

from functools import reduce

from ieml.ieml_objects.sentences import SuperSentence, Sentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word
from ieml.paths.constants import COORDINATES_KINDS, KIND_TO_RANK
from ieml.paths.exceptions import PathError

Context = namedtuple("Context", ['accept', 'conserve', 'switch'])

COORDINATES_CONTEXTS = {
    't': Context(accept={Text}, conserve=False, switch={
        Text: {SuperSentence, Sentence, Word, Term}
    }),
    'a': Context(accept={SuperSentence, Sentence}, conserve=True, switch={
        SuperSentence: {Sentence},
        Sentence: {Word}
    }),
    's': Context(accept={SuperSentence, Sentence}, conserve=True, switch={
        SuperSentence: {Sentence},
        Sentence: {Word}
    }),
    'm': Context(accept={SuperSentence, Sentence}, conserve=False, switch={
        SuperSentence: {Sentence},
        Sentence: {Word}
    }),
    'r': Context(accept={Word}, conserve=False, switch={
        Word: {Term}
    }),
    'f': Context(accept={Word}, conserve=False, switch={
        Word: {Term}
    })
}




class Path:
    def __init__(self, children):
        try:
            children = list(children)
        except TypeError:
            raise ValueError("The children must be iterable.")

        if any(not isinstance(child, Path) for child in children):
            raise ValueError('The children must be path instances.')

        # children unfold
        _children = []
        for c in children:
            if isinstance(c, self.__class__):
                _children += c.children
            else:
                if len(c.children) == 1:
                    _children.append(c.children[0])
                else:
                    _children.append(c)

        self.children = tuple(_children)
        self.cardinal = None
        self._development = None

    def develop(self):
        if self._development is None:
            if self.cardinal == 1:
                self._development = (self,)
            else:
                self._development = self._develop()

        return self._development

    def _develop(self):
        raise NotImplemented

    def _resolve_context(self):
        if isinstance(self, Coordinate):
            self.context = COORDINATES_CONTEXTS[self.kind]
            return

        development = self.develop()
        # the development is either a mul of coords or a context of mul and coords

        accept = set()
        switch = defaultdict(set)
        conserve = False

        for d in development:
            if isinstance(d, Coordinate):
                accept |= d.context.accept
                conserve = conserve or d.context.conserve
                for c in d.context.accept:
                    switch[c] |= d.context.switch[c]

            elif isinstance(d, MultiplicativePath):
                # must ensure that the context is conserved until the last element
                for ctx in d.children[0].context.accept:
                    for c in d.children[:-1]:
                        # if the coord not conserve the current context
                        if not c.context.conserve:
                            raise PathError("Invalid developed path, context discontinuity.", d)

                        if ctx not in c.context.accept:
                            # the context is lost
                            break
                    else:
                        last = d.children[-1].context
                        # check the last coord if it accept the element
                        if ctx in last.accept:
                            # if the last element conserve the context, set it to true (at least one path conserve)
                            conserve = conserve or last.conserve

                            # add the passed type to the accept list
                            accept |= {ctx}

                            # add the switch of the last element
                            switch[ctx] |= last.switch[ctx]

            else:
                # instance of context path
                for str_acc in d.children[0].context.accept:
                    stack = {str_acc}
                    for c in d.children:
                        _stack = set()
                        for s in stack:
                            if s in c.context.accept:
                                _stack |= c.context.switch[s]

                        if not _stack:
                            break

                        stack = _stack
                    else:
                        accept |= {str_acc}
                        switch[str_acc] |= stack

        if not accept:
            raise PathError("No context match this path.", self)

        self.context = Context(accept=accept, conserve=conserve, switch=dict(switch))

    def __mul__(self, other):
        if isinstance(other, str):
            from .tools import path
            other = path(other)

        if isinstance(other, Path):
            return ContextPath([self, other])

        raise NotImplemented

    def __add__(self, other):
        if isinstance(other, str):
            from .tools import path
            other = path(other)

        if isinstance(other, Path):
            return AdditivePath([self, other])

        raise NotImplemented


class ContextPath(Path):
    def __init__(self, children):
        if not children:
            raise ValueError('Must be a non empty children.')

        super().__init__(children)

        if len(self.children) < 2:
            raise ValueError("A context path must have at least two children.")

        self.cardinal = reduce(mul, [c.cardinal for c in self.children])
        self._resolve_context()

    def __str__(self):
        result = []
        for c in self.children:
            if isinstance(c, AdditivePath):
                result.append('(%s)'%str(c))
            else:
                result.append(str(c))

        return ':'.join(result)

    def _develop(self):
        return tuple(ContextPath(p) for p in product(*[c.develop() for c in self.children]))


class AdditivePath(Path):
    def __init__(self, children):
        if not children:
            raise ValueError('Must be a non empty children.')

        super().__init__(children)

        self.cardinal = sum(c.cardinal for c in self.children)
        self._resolve_context()

    def __str__(self):
        return '+'.join(map(str, self.children))

    def _develop(self):
        return tuple(chain.from_iterable(c.develop() for c in self.children))


class MultiplicativePath(Path):
    def __init__(self, children):
        if not children:
            raise ValueError('Must be a non empty children.')

        super().__init__(children)

        self.cardinal = reduce(mul, [c.cardinal for c in self.children])

        self._resolve_context()

    def __str__(self):
        result = ''
        for c in self.children:
            if isinstance(c, AdditivePath):
                result += '(%s)'%str(c)
            else:
                result += str(c)

        return result

    def _develop(self):
        return tuple(MultiplicativePath(p) for p in product(*[c.develop() for c in self.children]))


class Coordinate(Path):
    def __init__(self, kind, index=None):

        if not isinstance(kind, str) or not len(kind) == 1 or not kind in COORDINATES_KINDS:
            raise ValueError("A coordinate kind must be one of the following (%s)."%
                             ', '.join(map(str, COORDINATES_KINDS)))

        self.kind = kind

        if index is not None:
            if not isinstance(index, int):
                raise ValueError("Coordinate index must be int.")

            self.index = index
        else:
            self.index = None

        # no children
        super().__init__(())

        self.cardinal = 1

        self._resolve_context()

    def __str__(self):
        return self.kind + (str(self.index) if self.index is not None else '')

