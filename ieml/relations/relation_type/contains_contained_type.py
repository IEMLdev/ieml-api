from ieml.relations.relation_type.constants import CONTAINED_PM, CONTAINS_PM
from ieml.relations.relation_type.relation_type import RelationType
from ieml.usl import USL


class ContainsContainedRelationType(RelationType):
    def __call__(self, arg0: USL, arg1: USL):
        if arg1.singular_sequences_set.issubset(arg0.singular_sequences_set):
            return CONTAINS_PM
        elif arg0.singular_sequences_set.issubset(arg1.singular_sequences_set):
            return CONTAINED_PM


    # def iter_relations(self, arg0: USL):
    #     raise NotImplementedError()
    #
