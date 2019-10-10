import itertools
from typing import List

from ieml.dictionary.script import Script
from ieml.usl import USL, PolyMorpheme, check_polymorpheme
from ieml.usl.constants import ADDRESS_SCRIPTS, ACTANTS_SCRIPTS, ADDRESS_PROCESS_VALENCE_SCRIPTS, \
    check_lexeme_scripts, SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT, SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT, \
    SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT, DEPENDANT_QUALITY


def check_lexeme(lexeme, role=None):
    for pm in [lexeme.pm_address, lexeme.pm_content, lexeme.pm_transformation]:
        if not isinstance(pm, PolyMorpheme):
            raise ValueError("Invalid arguments to create a Lexeme, expects a Polymorpheme, not a {}."
                             .format(pm.__class__.__name__))

        check_polymorpheme(pm)

    check_lexeme_scripts(lexeme.pm_address.constant,
                         lexeme.pm_content.constant,
                         lexeme.pm_transformation.constant,
                         role=role)


def class_from_address(address):
    if any(s in ADDRESS_PROCESS_VALENCE_SCRIPTS for s in address.constant):
        return SYNTAGMATIC_FUNCTION_PROCESS_TYPE_SCRIPT
    elif any(s in ACTANTS_SCRIPTS + [DEPENDANT_QUALITY] for s in address.constant):
        return SYNTAGMATIC_FUNCTION_ACTANT_TYPE_SCRIPT
    else:
        return SYNTAGMATIC_FUNCTION_QUALITY_TYPE_SCRIPT


class Lexeme(USL):
    """A lexeme without the PA of the position on the tree (position independant lexeme)"""
    def __init__(self, pm_address: PolyMorpheme, pm_content: PolyMorpheme, pm_transformation: PolyMorpheme):
        super().__init__()
        self.pm_address = pm_address
        self.pm_content = pm_content
        self.pm_transformation = pm_transformation

        self.address = PolyMorpheme(constant=[m for m in pm_address.constant if m in ADDRESS_SCRIPTS])
        self.grammatical_class = self.pm_content.grammatical_class

        self._str = ""
        for pm in [self.pm_address, self.pm_content, self.pm_transformation]:
            if not pm.constant:
                break
            self._str += "({})".format(str(pm))

    def __lt__(self, other):
        return self.address < other.address or (self.address == other.address and
               (self.pm_address < other.pm_address or
               (self.pm_address == other.pm_address and self.pm_content and other.pm_content and self.pm_content < other.pm_content) or
               (self.pm_address == other.pm_address and self.pm_content == other.pm_content and
                self.pm_transformation and other.pm_transformation and self.pm_transformation < other.pm_transformation)))

    def _compute_singular_sequences(self):
        if self.pm_address.is_singular and (self.pm_content is None or self.pm_content.is_singular) and \
                (self.pm_transformation is None or self.pm_transformation.is_singular):
            return [self]
        else:
            _product = [self.pm_address,
                        self.pm_content,
                        self.pm_transformation]
            _product = [p.singular_sequences for p in _product if p is not None]

            return [Lexeme(*ss)
                    for ss in itertools.product(*_product)]

    def append_address(self, position: List[Script]):
        pm_address = PolyMorpheme(constant=list(self.pm_address.constant) + position, groups=self.pm_address.groups)
        return Lexeme(pm_address=pm_address,
                      pm_content=self.pm_content,
                      pm_transformation=self.pm_transformation)
