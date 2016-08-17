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

    "Ancestors in mode": FATHER_RELATION + '.' + MODE,
    "Ancestors in attribute": FATHER_RELATION + '.' + ATTRIBUTE,
    "Ancestors in substance": FATHER_RELATION + '.' + SUBSTANCE,

    "Descendents in mode": CHILD_RELATION + '.' + MODE,
    "Descendents in attribute": CHILD_RELATION + '.' + ATTRIBUTE,
    "Descendents in substance": CHILD_RELATION + '.' + SUBSTANCE,


    "Contained in": CONTAINED_RELATION,
    "Belongs to Paradigm": 'ROOT',
    "Contains": CONTAINS_RELATION
})
