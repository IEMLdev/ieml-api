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
    """

    :param paradigms_list: list of all the root paradigms in our database
    :param usl_list: the usl collection we want to analyse
    :return:the ordered list of the root paradigms the most cited by the usl_list
    """


    #Un classement des paradigmes-racine selon leur score de citation (décomposé en noms, verbes, auxiliaires)
    # --> on a oublié la décomposition du score en fonction de nom, verb et aux !!
    # est ce que Pierre veut que l'on sache par ex que le paradigme racine le + cité avec un score de 7,
    # a obtenu ce score grace à 4 nom, 2 aux et 1 verb ?

    paradigms = {p:0 for p in paradigms_list}
    for usl in usl_list:
        term_list = [term for term in usl.tree_iter() if isinstance(term, Term)]
        for term in term_list:
            #  TODO : CHECK IF PARADIGM_LIST CONTAINS TERM OBJECT OR STRINGS
            # --> les paradigmes semblent etre des strings
            for paradigm in paradigms_list:
                p_term = Term(sc(paradigm))
                #if set(term.script.singular_sequences) <= set(paradigm.script.singular_sequences):
                if set(term.script.singular_sequences) <= set(p_term.script.singular_sequences):
                    paradigms[paradigm] += 1

    return sorted(paradigms, key= lambda e: paradigms[e])
    # ca retourne une liste


# 3 Pour chaque paradigme-racine, une liste ordonnée des USLs qui le citent le plus
def rank_usls(paradigms_list, usl_list):
    paradigm_dico = {p:[] for p in paradigms_list}



