from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from ieml.script import CONTAINED_RELATION
from bidict import bidict
from models.relations import RelationsConnector, RelationsQueries
from fractions import Fraction
from collections import namedtuple
from ieml.calculation.distance import get_grammar_class
import ieml.AST.terms
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS

ScoreNode = namedtuple('ScoreNode', ['script', 'score'])


def rank_paradigms(paradigms_list, usl_list):
    """

    :param paradigms_list: list of all the root paradigms in our database
    :param usl_list: the usl collection we want to analyse
    :return:the ordered list of the root paradigms the most cited by the usl_list,
    first element of the list is the most cited root paradigm, and the dictionary of paradigms which associates a list
    list[0] : score of thr root paradigm, list[1] : number of noun citing the root paradigm
    list[2] : number of aux citing the root paradigm, list[3] : number of verb citing the root paradigm
    """
    paradigms = {p:[0,0,0,0] for p in paradigms_list}
    #paradigms = {p:0 for p in paradigms_list}
    # value is a list of 4 elements which correspond to :
    # a- how many times the root paradigm p is cited
    # b- number of noun citing p
    # c- number of auxiliary citing p
    # d- number of verb citing p
    # so a = b + c + d

    for usl in usl_list:
        term_list = [term for term in usl.tree_iter() if isinstance(term, Term)]
        for term in term_list:
            for paradigm in paradigms_list:
                p_term = Term(sc(paradigm))
                if set(term.script.singular_sequences) <= set(p_term.script.singular_sequences):
                    paradigms[paradigm][0] += 1
                    # verifify the grammatical of the term citing the root paradigm
                    if term.grammatical_class == 2: # noun
                        paradigms[paradigm][1] += 1
                    elif term.grammatical_class == 0: # aux
                        paradigms[paradigm][2] += 1
                    elif term.grammatical_class == 1: # verb
                        paradigms[paradigm][3] += 1


    # we remove the root paradigms which are not cited by usl_list
    for p in paradigms_list:
        if paradigms[p][0] == 0:
       # if paradigms[p] == 0:
            del paradigms[p]

    return sorted(paradigms, key= lambda e: paradigms[e][0], reverse=True), paradigms


# 3 Pour chaque paradigme-racine, une liste ordonnée des USLs qui le citent le plus
def rank_usls(paradigms_list, usl_list):
    #paradigm_dico = {p:[] for p in paradigms_list}
    pass

if __name__ == '__main__':
        # These 2 terms have the same root paradigm : E:E:F:.
        term_1 = Term(sc("E:E:F:."))
        term_2 = Term(sc("E:E:M:."))

        usl_list = [term_1, term_2]
        paradigms_list = ["E:F:.O:O:.-", "E:F:.M:M:.-", "E:E:F:."]

        dico_test = rank_paradigms(paradigms_list,usl_list)
