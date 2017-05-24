from bidict import bidict
from ieml.ieml_objects.dictionary import RELATION_TYPES_TO_INDEX


relation_name_table = bidict({
    "Crossed siblings": "CROSSED",
    "Associated siblings": "ASSOCIATED",
    "Twin siblings": "TWIN",
    "Opposed siblings": "OPPOSED",

    # ancestor : Etymologie
    "Ancestors in mode": "FATHER.MODE",
    "Ancestors in attribute": "FATHER.ATTRIBUTE",
    "Ancestors in substance": "FATHER.SUBSTANCE",

    "Descendents in mode": "CHILDREN.MODE",
    "Descendents in attribute": "CHILDREN.ATTRIBUTE",
    "Descendents in substance": "CHILDREN.SUBSTANCE",

    # Hyperonymes
    "Contained in": "CONTAINED",
    "Belongs to Paradigm": 'ROOT',
    # Hyponymes
    "Contains": "CONTAINS"
})

relations_order = {
    "Crossed siblings": 4,
    "Associated siblings": 2,
    "Twin siblings": 3,
    "Opposed siblings": 1,

    # ancestor : Etymologie
    "Ancestors in mode": 12,
    "Ancestors in attribute": 11,
    "Ancestors in substance": 10,

    "Descendents in mode": 9,
    "Descendents in attribute": 8,
    "Descendents in substance": 7,

    # Hyperonymes
    "Contained in": 6,
    "Belongs to Paradigm": 0,
    # Hyponymes
    "Contains": 5
}