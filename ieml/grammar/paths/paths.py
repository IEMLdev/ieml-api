from _operator import mul
from collections import namedtuple, defaultdict
from itertools import chain, product

from functools import reduce

from ...grammar import Theory, Fact, Text, Word, Topic
from .constants import COORDINATES_KINDS
from ...exceptions import PathError

Context = namedtuple("Context",
                     ['accept',   # the types this context can deference
                      'conserve', # if this context must immediately switch to a lower type (mode and morphems)
                      'switch'])  # the mapping type -> type this context can switch

COORDINATES_CONTEXTS = {
    't': Context(accept={Text}, conserve=False, switch={
        Text: {Theory, Fact, Topic, Word}
    }),
    'a': Context(accept={Theory, Fact}, conserve=True, switch={
        Theory: {Fact},
        Fact: {Topic}
    }),
    's': Context(accept={Theory, Fact}, conserve=True, switch={
        Theory: {Fact},
        Fact: {Topic}
    }),
    'm': Context(accept={Theory, Fact}, conserve=False, switch={
        Theory: {Fact},
        Fact: {Topic}
    }),
    'r': Context(accept={Topic}, conserve=False, switch={
        Topic: {Word}
    }),
    'f': Context(accept={Topic}, conserve=False, switch={
        Topic: {Word}
    })
}


class Path:
    # represent a path.
    # A path is an element of the form
    # this correspond to a descent in an ieml tree
    #
    # 't0:sa0:r0'
    # 't:s:(r0+f1)'
    # 't:(sm0+sa0:m0):r1'
    # '(t0+t1):s:s:f'
    #
    # A path have a context, the types of ieml-object that this path can deference.
    # The type of the ieml_object inferred by this path on a well typed ieml-object is determined by the context at the
    # end of the string.
    #
    # There are 5 different context, for each ieml-object type. A context switch occur with ':'.
    # - the Text context :
    #    't' is the only literal. If indexed like 'tn' where 'n' is an integer, it represent the n-th element in the
    # text object. This context allow only one character ('t' or 'tn') then it is always followed by ':' or nothing.
    # It can be followed by a super-Fact, a Fact or a Topic context.
    #
    # - the Super Fact and Fact ctx:
    # Begin with 's' or 'sn' but if the 'n' is an integer, it will be ignored. Can be followed by 'an' or 'mn'
    # where 'n' is an integer. When it is followed by 'an' it lead to the the n-th attribute of the current node. Same
    # for 'mn', but for the mode of the n-th attribute (the clause of this node, the n-th attribute and his mode). If
    # it is a mode, it can only be followed by a context switch ':'.
    # Theory lead to Fact ctx and Fact to Topic ctx.
    #
    # - the Topic context:
    # Only one literal of the form 'r' | 'rn' | 'f' | 'fn' where 'n' is an integer. These literal cannot be followed by
    # another character. If 'r' it lead all the root terms (the morphem), 'rn' lead only the n-th in the root morphem.
    # Same for 'f'|'fn' and the flexing morphem.
    #
    #  Ex: 't0:sa0:r' -> In a text context (or usl), the first element of the text, which is a Fact,
    #  then in a Fact context, the topic of the first attribute of the root (index on 's' is ignored),
    #  then in a topic context, the roots terms.
    #
    #
    #
    # the context of a path can be accessed:
    #   p.context.accept is a set of accepted types to deference
    #   p.context.switch is a dict of accepted types to inferred types i.e. the type of b = a[p] where a type is in
    # p.context.accept. len(p.context.switch) == len(p.context.accept)
    #
    # We add the '+' notation. An additive path is defined by the sum of multiple paths.
    # To get the list of sub path : p.develop
    #
    # p.cardinal == len(p.develop)
    #
    #

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
        self.context = None

    @property
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

        # the development is either a mul of coords or a context of mul and coords
        accept = set()
        switch = defaultdict(set)
        conserve = False

        for d in self.develop:
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

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.__str__())


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
        return tuple(ContextPath(p) for p in product(*[c.develop for c in self.children]))


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
        return tuple(chain.from_iterable(c.develop for c in self.children))


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
        return tuple(MultiplicativePath(p) for p in product(*[c.develop for c in self.children]))


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

