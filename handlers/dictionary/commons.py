from bidict import bidict


relation_name_table = bidict({
    "Crossed siblings": "crossed",
    "Associated siblings": "associated",
    "Twin siblings": "twin",
    "Opposed siblings": "opposed",

    # ancestor : Etymology
    "Ancestors in mode": "father_mode",
    "Ancestors in attribute": "father_attribute",
    "Ancestors in substance": "father_substance",

    "Descendents in mode": "child_mode",
    "Descendents in attribute": "child_attribute",
    "Descendents in substance": "child_substance",

    # Hyperonymes
    "Contained in": "contained",
    "Belongs to Paradigm": 'ROOT',
    # Hyponymes
    "Contains": "contains"
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