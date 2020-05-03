from ieml.relations.relation_type.constants import GENUS_PM, SPECIES_PM
from ieml.relations.relation_type.relation_type import RelationType
from ieml.usl import USL


class GenusSpeciesRelationType(RelationType):
    def __call__(self, arg0: USL, arg1: USL):
        if arg1 in arg0:
            return GENUS_PM
        elif arg0 in arg1:
            return SPECIES_PM

    # def iter_relations(self, arg0: USL):
    #     raise NotImplementedError()

