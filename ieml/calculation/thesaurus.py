from collections import namedtuple

from ieml.object.terms import Term

ScoreNode = namedtuple('ScoreNode', ['parser', 'score'])


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

