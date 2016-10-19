import functools
from bidict import bidict
from models.terms.terms import TermsConnector
from ieml.script.constants import OPPOSED_SIBLING_RELATION, ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, \
    TWIN_SIBLING_RELATION, FATHER_RELATION, SUBSTANCE, ATTRIBUTE, MODE, CHILD_RELATION, CONTAINED_RELATION, \
    CONTAINS_RELATION

def terms_db():
    return TermsConnector()


relation_name_table = bidict({
    "Crossed siblings": CROSSED_SIBLING_RELATION,
    "Associated siblings": ASSOCIATED_SIBLING_RELATION,
    "Twin siblings": TWIN_SIBLING_RELATION,
    "Opposed siblings": OPPOSED_SIBLING_RELATION,

    # ancestor : Etymologie
    "Ancestors in mode": FATHER_RELATION + '.' + MODE,
    "Ancestors in attribute": FATHER_RELATION + '.' + ATTRIBUTE,
    "Ancestors in substance": FATHER_RELATION + '.' + SUBSTANCE,

    "Descendents in mode": CHILD_RELATION + '.' + MODE,
    "Descendents in attribute": CHILD_RELATION + '.' + ATTRIBUTE,
    "Descendents in substance": CHILD_RELATION + '.' + SUBSTANCE,

    # Hyperonymes
    "Contained in": CONTAINED_RELATION,
    "Belongs to Paradigm": 'ROOT',
    # Hyponymes
    "Contains": CONTAINS_RELATION
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