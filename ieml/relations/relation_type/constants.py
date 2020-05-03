from ieml.dictionary.script import script
from ieml.usl import PolyMorpheme, USL

SPECIES_PM = PolyMorpheme(constant=[script('E:S:.d.-')]) # espèce
GENUS_PM = PolyMorpheme(constant=[script('E:T:.d.-')]) # genre

CONTAINED_PM = PolyMorpheme(constant=[script('E:S:.j.-')]) # ensemble
CONTAINS_PM = PolyMorpheme(constant=[script('E:S:.g.-')]) # élément

COMPOSED_PM = PolyMorpheme(constant=[script('E:T:.j.-')]) # structure / cause formelle
# COMPOSED_PM = PolyMorpheme(constant=[script('E:S:.g.-')]) # élément



RelationType = USL
relation_types_to_id = {
    SPECIES_PM: 'species',
    GENUS_PM: 'genus',
    CONTAINS_PM: 'contains',
    CONTAINED_PM: 'contained',
    COMPOSED_PM: 'composed'
}
relation_types = list(relation_types_to_id)
id_to_relation_types = {
    v: k for k, v in relation_types_to_id.items()
}