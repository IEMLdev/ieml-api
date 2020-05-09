from typing import Union

from sqlalchemy.util import NoneType

from ieml.usl import USL
from ieml.usl.usl import usl


class RelationType:
    def __init__(self, name: str, usl: USL):
        self.name = name
        self.usl = usl

    def __hash__(self):
        return hash(self.name)

# AXIOMATIC RELATIONSHIPS
# TODO add USLs IEML

ALIGNMENT_RELATION_USL = RelationType(name='alignment', usl=usl(""))
ALIGNMENT_RELATION_USL_MATCH = RelationType(name='alignment_match', usl=usl(""))
ALIGNMENT_RELATION_USL_MATCH_EXACT = RelationType(name='alignment_match_exact', usl=usl(""))
ALIGNMENT_RELATION_USL_MATCH_CLOSE = RelationType(name='alignment_match_close', usl=usl(""))

DESCRIPTOR_RELATION_USL = RelationType(name='descriptor', usl=usl(""))

DESCRIPTOR_RELATION_USL_TRANSLATION = RelationType(name='descriptor_translation', usl=usl(""))
DESCRIPTOR_RELATION_USL_TAG = RelationType(name='descriptor_tag', usl=usl(""))
DESCRIPTOR_RELATION_USL_COMMENT = RelationType(name='descriptor_comment', usl=usl(""))

SYNTAX_RELATION_USL = RelationType(name='syntax', usl=usl(""))

SYNTAX_RELATION_USL_PM_CONTAINS = RelationType(name='syntax_contains', usl=usl('E:S:.g.-'))

SYNTAX_RELATION_USL_COMPOSED = RelationType(name='syntax_composed', usl=usl(""))

SYNTAX_RELATION_PM_USL_COMPOSED = RelationType(name='syntax_composed_pm', usl=usl(""))
SYNTAX_RELATION_PM_CONSTANT_USL_COMPOSED = RelationType(name='syntax_composed_pm_constant', usl=usl(""))
SYNTAX_RELATION_PM_GROUP0_USL_COMPOSED = RelationType(name='syntax_composed_pm_group0', usl=usl(""))
SYNTAX_RELATION_PM_GROUP1_USL_COMPOSED = RelationType(name='syntax_composed_pm_group1', usl=usl(""))
SYNTAX_RELATION_PM_GROUP2_USL_COMPOSED = RelationType(name='syntax_composed_pm_group2', usl=usl(""))

SYNTAX_RELATION_LEX_USL_COMPOSED = RelationType(name='syntax_composed_lex', usl=usl(""))
SYNTAX_RELATION_LEX_CONTENT_USL_COMPOSED = RelationType(name='syntax_composed_lex_content', usl=usl(""))
SYNTAX_RELATION_LEX_FLEXING_USL_COMPOSED = RelationType(name='syntax_composed_lex_flexing', usl=usl(""))


SYNTAX_RELATION_SYNFUN_USL_COMPOSED = RelationType(name='syntax_composed_synfun', usl=usl(""))
SYNTAX_RELATION_SYNFUN_ROOT_USL_COMPOSED = RelationType(name='syntax_composed_synfun_root', usl=usl(""))
SYNTAX_RELATION_SYNFUN_INITIATOR_USL_COMPOSED = RelationType(name='syntax_composed_synfun_initiator', usl=usl(""))
SYNTAX_RELATION_SYNFUN_INTERACTANT_USL_COMPOSED = RelationType(name='syntax_composed_synfun_interactant', usl=usl(""))
SYNTAX_RELATION_SYNFUN_RECEIVER_USL_COMPOSED = RelationType(name='syntax_composed_synfun_receiver', usl=usl(""))

SYNTAX_RELATION_SYNFUN_TIME_USL_COMPOSED = RelationType(name='syntax_composed_synfun_time', usl=usl(""))
SYNTAX_RELATION_SYNFUN_LOCATION_USL_COMPOSED = RelationType(name='syntax_composed_synfun_location', usl=usl(""))

SYNTAX_RELATION_SYNFUN_MANNER_USL_COMPOSED = RelationType(name='syntax_composed_synfun_manner', usl=usl(""))
SYNTAX_RELATION_SYNFUN_INTENTION_USL_COMPOSED = RelationType(name='syntax_composed_synfun_intention', usl=usl(""))
SYNTAX_RELATION_SYNFUN_CAUSE_USL_COMPOSED = RelationType(name='syntax_composed_synfun_cause', usl=usl(""))


SYNTAX_RELATION_WORD_USL_COMPOSED = RelationType(name='syntax_composed_word', usl=usl(""))
SYNTAX_RELATION_WORD_SYNFUN_USL_COMPOSED = RelationType(name='syntax_composed_word_synfun', usl=usl(""))
SYNTAX_RELATION_WORD_ROLE_USL_COMPOSED = RelationType(name='syntax_composed_word_role', usl=usl(""))

SYNTAX_RELATION_MORPHEME_USL_COMPOSED = RelationType(name='syntax_composed_morpheme', usl=usl(""))
SYNTAX_RELATION_MORPHEME_FATHER_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_father', usl=usl(""))
SYNTAX_RELATION_MORPHEME_FATHER_SUBSTANCE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_father_substance', usl=usl(""))
SYNTAX_RELATION_MORPHEME_FATHER_ATTRIBUTE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_father_attribute', usl=usl(""))
SYNTAX_RELATION_MORPHEME_FATHER_MODE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_father_mode', usl=usl(""))
SYNTAX_RELATION_MORPHEME_CHILD_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_child', usl=usl(""))
SYNTAX_RELATION_MORPHEME_CHILD_SUBSTANCE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_child_substance', usl=usl(""))
SYNTAX_RELATION_MORPHEME_CHILD_ATTRIBUTE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_child_attribute', usl=usl(""))
SYNTAX_RELATION_MORPHEME_CHILD_MODE_USL_COMPOSED = RelationType(name='syntax_composed_morpheme_child_mode', usl=usl(""))
