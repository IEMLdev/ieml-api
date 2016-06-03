from ieml.AST.commons import TreeStructure
from .constants import LAYER_MARKS, PRIMITVES, remarkable_multiplication_lookup_table, REMARKABLE_ADDITION, character_value
import itertools



class Script(TreeStructure):
    """ A script is defined by a character (PRIMITIVES, REMARKABLE_ADDITION OR REMARKABLE_MULTIPLICATION)
     or a list of script children. All the element in the children list must be an AdditiveScript or
     a MultiplicativeScript."""
    def __init__(self, children=None, character=None):
        super().__init__()

        if children:
            self.children = children
        else:
            self.children = []

        if character:
            self.character = character
        else:
            self.character = None

        # Layer of this script
        self.layer = None

        # If it is a a paradigm
        self.paradigm = None

        # If the script is composed with E
        self.empty = None

        # The number of singular sequence (if paradigm it is one, self)
        self.cardinal = None

        # The singular sequences
        self.singular_sequences = None

    def __gt__(self, other):
        return self != other and not self.__lt__(other)

    def __lt__(self, other):
        if not isinstance(self, Script) or not isinstance(other, Script):
            raise NotImplemented()

        if self == other:
            return False

        if self.layer != other.layer:
            # order by layer
            return self.layer < other.layer
        else:
            if self.cardinal != other.cardinal:
                # then by number of singular sequence
                return self.cardinal < other.cardinal
            else:
                if self.layer != 0:
                    # layer != 0 => children is set, no children are for layer 0 (MultiplicativeScript)
                    if isinstance(self, other.__class__):
                        # if they are the same class
                        # Compare the children in alphabetical order
                        iterator = iter(other.children)
                        for s in self.children:
                            try:
                                o = iterator.next()
                                if o != s:
                                    return s < o
                            except StopIteration:
                                return False
                        # self have fewer elements, all equals to the first of other's children, self is lower.
                        return True
                    else:
                        # not an instance, one is multiplicative, other one is additive
                        # They have the same number of singular sequence so the multiplicative is fewer :
                        # each variable of the addition have less singular sequence than the multiplication script
                        return isinstance(self, MultiplicativeScript)
                else:
                    # Layer 0
                    # Compare the value of the character or the sum
                    self_char_value = None
                    if isinstance(self, AdditiveScript):
                        # The character value is the sum of all character of the addition
                        self_char_value = sum((character_value[c.character] for c in self.children))
                    else:
                        self_char_value = character_value[self.character]

                    other_char_value = None
                    if isinstance(other, AdditiveScript):
                        # The character value is the sum of all character of the addition
                        other_char_value = sum((character_value[c.character] for c in other.children))
                    else:
                        other_char_value = character_value[other.character]

                    return self_char_value < other_char_value

class AdditiveScript(Script):
    """ Represent an addition of same layer scripts."""
    def __init__(self, children=None, character=None):
        super().__init__(children=children, character=character)

    def _do_checking(self):
        if self.character: #  remarkable addition
            self.layer = 0
            self.empty = False
            self.paradigm = True
            self.cardinal = len(REMARKABLE_ADDITION[self.character])
            # extends the character
            self.children = REMARKABLE_ADDITION_SCRIPT[self.character]
        else:
            self.layer = self.children[0].layer
            self.empty = all((e.empty for e in self.children))
            self.paradigm = len(self.children) > 1 or any(child.paradigm for child in self.children)
            self.cardinal = sum((e.cardinal for e in self.children))

    def _do_precompute_str(self):
        self._str = (self.character + LAYER_MARKS[0]) if self.character is not None \
            else '+'.join(map(str, self.children))

    def _do_ordering(self):
        # Ordering of the children
        self.children.sort()

        # Generating the singular sequence
        if not self.paradigm:
            self.singular_sequences = [self]
        else:
            # additive proposition has always children set
            self.singular_sequences = [sequence for child in self.children for sequence in child.singular_sequences]


class MultiplicativeScript(Script):
    """ Represent a multiplication of three scripts of the same layer."""
    def __init__(self, substance=None, attribute=None, mode=None, character=None):
        if substance is not None:
            if attribute is not None:
                if mode is not None:
                    children = (substance, attribute, mode)
                else:
                    children = (substance, attribute)
            else:
                children = (substance,)
        else:
            children = None

        super().__init__(children=children, character=character)

    def _do_precompute_str(self):
        self._str = (self.character if self.character is not None
            else ''.join(map(str, self.children))) + LAYER_MARKS[self.layer]


    def _do_checking(self):
        # Computation of layer, paradigm and emptiness
        if self.character:
            self.layer = 0 if self.character in PRIMITVES else 1
            self.empty = self.character == 'E'
            self.paradigm = False
            self.cardinal = 1
        else:
            self.layer = self.children[0].layer + 1
            self.empty = all((e.empty for e in self.children))
            self.paradigm = any((e.paradigm for e in self.children))

            self.cardinal = 1
            for e in self.children:
                self.cardinal = self.cardinal * e.cardinal

        # Use of remarkable mutliplication
        if self.children and self.layer == 1:
            children_str = ''.join(map(str, self.children))
            if children_str in remarkable_multiplication_lookup_table:
                self.character = remarkable_multiplication_lookup_table[children_str]

        # expends the character of layer 1
        if self.layer == 1 and self.character is not None:
            self.children = REMARKABLE_MULTIPLICATION_SCRIPT[self.character]

        # Reduction of empty
        if self.children:
            if len(self.children) == 3 and self.children[2].empty:
                if self.children[1].empty:
                    self.children = (self.children[0],)
                else:
                    self.children = (self.children[0], self.children[1])

            if len(self.children) == 2 and self.children[1].empty:
                self.children = (self.children[0],)

            # TODO : delete stages of single element addition
            # for i in range(0, len(self.children)):
            #     if isinstance(self.children[i], AdditiveScript) and len(self.children[i].children) == 1:
            #         self.children[i] = self.children[i].children[0]

    def _do_ordering(self):
        # Generate the singular sequence
        if not self.paradigm:
            self.singular_sequences = [self]
        else:
            children_sequences = (self.children[0].singular_sequences,)
            if len(self.children) > 1:
                children_sequences += (self.children[1].singular_sequences,)
                if len(self.children) > 2:
                    children_sequences += (self.children[2].singular_sequences,)

            self.singular_sequences = []
            for triplet in itertools.product(*children_sequences):
                if len(triplet) == 3:
                    sequence = MultiplicativeScript(substance=triplet[0], attribute=triplet[1], mode=triplet[2])
                elif len(triplet) == 2:
                    sequence = MultiplicativeScript(substance=triplet[0], attribute=triplet[1])
                else:
                    sequence = MultiplicativeScript(substance=triplet[0])

                sequence.check()
                self.singular_sequences.append(sequence)


# Building the remarkable multiplication to script
REMARKABLE_MULTIPLICATION_SCRIPT = {
    "wo": (MultiplicativeScript(character='U'), MultiplicativeScript(character='U')),
    "wa": (MultiplicativeScript(character='U'), MultiplicativeScript(character='A')),
    "y": (MultiplicativeScript(character='U'), MultiplicativeScript(character='S')),
    "o": (MultiplicativeScript(character='U'), MultiplicativeScript(character='B')),
    "e": (MultiplicativeScript(character='U'), MultiplicativeScript(character='T')),

    "wu": (MultiplicativeScript(character='A'), MultiplicativeScript(character='U')),
    "we": (MultiplicativeScript(character='A'), MultiplicativeScript(character='A')),
    "u": (MultiplicativeScript(character='A'), MultiplicativeScript(character='S')),
    "a": (MultiplicativeScript(character='A'), MultiplicativeScript(character='B')),
    "i": (MultiplicativeScript(character='A'), MultiplicativeScript(character='T')),

    "j": (MultiplicativeScript(character='S'), MultiplicativeScript(character='U')),
    "g": (MultiplicativeScript(character='S'), MultiplicativeScript(character='A')),
    "s": (MultiplicativeScript(character='S'), MultiplicativeScript(character='S')),
    "b": (MultiplicativeScript(character='S'), MultiplicativeScript(character='B')),
    "t": (MultiplicativeScript(character='S'), MultiplicativeScript(character='T')),

    "h": (MultiplicativeScript(character='B'), MultiplicativeScript(character='U')),
    "c": (MultiplicativeScript(character='B'), MultiplicativeScript(character='A')),
    "k": (MultiplicativeScript(character='B'), MultiplicativeScript(character='S')),
    "m": (MultiplicativeScript(character='B'), MultiplicativeScript(character='B')),
    "n": (MultiplicativeScript(character='B'), MultiplicativeScript(character='T')),

    "p": (MultiplicativeScript(character='T'), MultiplicativeScript(character='U')),
    "x": (MultiplicativeScript(character='T'), MultiplicativeScript(character='A')),
    "d": (MultiplicativeScript(character='T'), MultiplicativeScript(character='S')),
    "f": (MultiplicativeScript(character='T'), MultiplicativeScript(character='B')),
    "l": (MultiplicativeScript(character='T'), MultiplicativeScript(character='T'))
}

for key in REMARKABLE_MULTIPLICATION_SCRIPT:
    for e in REMARKABLE_MULTIPLICATION_SCRIPT[key]:
        e.check()

# Building the remarkable addition to script
REMARKABLE_ADDITION_SCRIPT = {}
for key in REMARKABLE_ADDITION:
    REMARKABLE_ADDITION_SCRIPT[key] = [MultiplicativeScript(character=c) for c in REMARKABLE_ADDITION[key]]
    for m in REMARKABLE_ADDITION_SCRIPT[key]:
        m.check()
