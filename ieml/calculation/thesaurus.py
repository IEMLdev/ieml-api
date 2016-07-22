import itertools as it
from collections import defaultdict
from ieml.AST.propositions import Word, Sentence, SuperSentence, Morpheme
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from ieml.script import CONTAINED_RELATION
from bidict import bidict
from models.relations import RelationsConnector, RelationsQueries
from fractions import Fraction
from collections import namedtuple


ScoreNode = namedtuple('ScoreNode', ['script', 'score'])


def rank_paradigms(paradigms_list, usl_list):
    paradigms = {p:0 for p in paradigms_list}
    for usl in usl_list:
        term_list = [term for term in usl.tree_iter() if isinstance(term, Term)]
        for term in term_list:
            #  TODO : CHECK IF PARADIGM_LIST CONTAINS TERM OBJECT OR STRINGS
            for paradigm in paradigms_list:
                if set(term.script.singular_sequences) <= set(paradigm.script.singular_sequences):
                    paradigms[paradigm] += 1

    # return sorted(list[paradigms], key= lambda e: paradigms[e])
    return sorted(paradigms, key= lambda e: paradigms[e])

