from ieml.AST.terms import Term
from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.script.tables import generate_tables
from ieml.operator import sc
from collections import namedtuple, defaultdict
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from models.terms import TermsConnector
import numpy as np

ScoreNode = namedtuple('ScoreNode', ['script', 'score'])
Cache = namedtuple('Cache', ['source_layer', 'source_class'])
ParadigmMetadata = namedtuple('ParadigmMetadata', ['paradigm', 'score', 'nouns', 'auxiliary', 'verb'])


def _build_cache(usl_collection):

    # For every term we associate a vector where each coordinate is the number of citations from a given layer
    # First coordinate: SuperSentence
    # Second coordinate: Sentence
    # Third coordinate: Word
    source_layer = defaultdict(lambda: [0, 0, 0])
    source_class = defaultdict(lambda: [0, 0, 0])

    for usl in usl_collection:
        for elem in usl.tree_iter():
            terms = [term for term in usl.tree_iter() if isinstance(term, Term)]
            for t in terms:
                source_layer[t.script][coordinate[elem.__class__]] += 1
                source_class[t.script][elem.grammatical_class] += 1

    return Cache(source_layer=source_layer, source_class=source_class)

_cache = None


def rank_paradigms(paradigm_list, usl_collection):
    """

    Parameters
    ----------
    paradigm_list
    usl_collection

    Returns
    -------

    """

    result = []
    global _cache
    if not _cache:
        _cache = _build_cache(usl_collection)

    for paradigm in paradigm_list:

        score = 0

        if _cache.source_layer[paradigm][0]:
            score = _cache.source_layer[paradigm][0] * layer_weight[SuperSentence]
        elif _cache.source_layer[paradigm][1]:
            score = _cache.source_layer[paradigm][1] * layer_weight[Sentence]
        elif _cache.source_layer[paradigm][2]:
            score = _cache.source_layer[paradigm][2] * layer_weight[Word]

        result.append(ParadigmMetadata(paradigm=paradigm, score=score,
                                       nouns=_cache.source_class[paradigm][NOUN_CLASS],
                                       auxiliary=_cache.source_class[paradigm][AUXILIARY_CLASS],
                                       verb=_cache.source_class[paradigm][VERB_CLASS]))

    return sorted(result, key=lambda x: x.score, reversed=True)


# 3 Pour chaque paradigme-racine, une liste ordonnée des USLs qui le citent le plus
def rank_usls(paradigms_list, usl_list):
    """

    :param paradigms_list: list of the root paradigms we want to analyse
    :param usl_list: list of the uls (a collection) we want to analyse
    :return:a dictionary whose keys are the paradigms of paradigms_list
    and the values : an ordered list of the usls (of usl_list) which most quote the paradigm
     (first element is usl which quotes the most the paradigm in key), the usls are converted into strings
     if in usl_list there is the same usl twice, in the returned dictionary this usl will appear only once
    """
    paradigm_dico = {p:[] for p in paradigms_list}
    for p in paradigms_list:
        p_term = Term(sc(p))
        usl_dico = {str(usl):0 for usl in usl_list}  # convert usl to string, to use a dictionary
        for usl in usl_list:
            term_list = [term for term in usl.tree_iter() if isinstance(term, Term)]
            for term in term_list:
                if set(term.script.singular_sequences) <= set(p_term.script.singular_sequences):
                    usl_dico[str(usl)] += 1

        # we remove the usls which do not quote the paradigm p
        for usl in usl_list:
            if str(usl) in usl_dico and usl_dico[str(usl)] == 0:
                del usl_dico[str(usl)]

        sorted_usls = sorted(usl_dico, key= lambda e: usl_dico[e], reverse=True)  #  this is a list
        for e in sorted_usls:
            paradigm_dico[p].append(e)

    return paradigm_dico


def rank_usl_terms(term_list, usl_collection):
    return {term: rank_usl_single_term(term, usl_collection) for term in term_list}


def rank_usl_single_term(term, usl_collection):
    """

    Parameters
    ----------
    term
    usl_collection

    Returns
    -------

    """

    # We will work with a term that is of type Script
    if isinstance(term, str):
        term = sc(term)
    elif isinstance(term, Term):
        term = term.script

    usl_id_map = {usl: i for i, usl in enumerate(usl_collection)}
    score_count = [0 for i in range(len(usl_collection))]

    for i, usl in enumerate(usl_collection):
        for elem in usl.tree_iter():
            # I'm checking singular sequence set equality because we can be sure it's the same term object if they
            # describe the same singular sequence set regardless if it is correctly factorized
            if isinstance(elem, Term) and elem.script.singular_sequences == term.singular_sequences:
                score_count[i] += 1

    return sorted(usl_collection, key=lambda e: score_count[usl_id_map[e]], reverse=True)


def paradigm_usl_distribution(paradigm, usl_collection):
    """

    Parameters
    ----------
    paradigm
    usl_collection

    Returns
    -------
    Distribution of number of terms (contained in 'paradigm') cited overlayed on the paradigms table
    """

    TermLocation = namedtuple('TermLocation', ['table', 'coords'])
    if isinstance(paradigm, str):
        paradigm = sc(paradigm)

    tbls = generate_tables(paradigm)
    term_coordinates = {}
    dist_tables = [np.zeros(table.cells.shape, dtype=int) for table in tbls]

    for term in paradigm.singular_sequences:
        for i, table in enumerate(tbls):
            if term in table.paradigm.singular_sequences:
                table_idx = i
                coord = np.where(table == term)
        term_coordinates[term] = TermLocation(table=table_idx, coords=coord)

    for usl in usl_collection:
        for elem in usl.tree_iter():
            if isinstance(elem, Term) and elem.script in term_coordinates:
                term_loc = term_coordinates[elem.script]
                if dist_tables[term_loc.table].ndim == 1:
                    dist_tables[term_loc.table][term_loc.coords[0][0]] += 1
                elif dist_tables[term_loc.table].ndim == 2:
                    dist_tables[term_loc.table][term_loc.coords[0][0]][term_loc.coords[1][0]] += 1
                elif dist_tables[term_loc.table].ndim == 3:
                    dist_tables[term_loc.table][term_loc.coords[0][0]][term_loc.coords[1][0]][term_loc.coords[2][0]] += 1

    return dist_tables


coordinate = {
    SuperSentence: 0,
    Sentence: 1,
    Word: 2
}


layer_weight = {
    Word: 1,
    Sentence: 2,
    SuperSentence: 3
}

if __name__ == '__main__':

    paradigms_list = ["E:E:F:.", "E:F:.M:M:.-", "E:F:.O:O:.-"]

    #These 2 terms have the same root paradigm : E:E:F:.
    term_1 = Term(sc("E:E:F:."))
    term_2 = Term(sc("E:E:M:."))

    #The root paradigm of term_3 is E:F:.M:M:.-
    term_3 = Term(sc("E:M:.k.-"))

    usl_list1 = [term_1, term_2]
    usl_list2 = [term_3, term_1, term_3]
    usl_list3 = [term_1, term_3, term_2]

    term_1.check()
    term_2.check()
    term_3.check()

    paradigm_dico = rank_usls(paradigms_list,usl_list1)
    tc = TermsConnector()
    full_root_paradigms = tc.root_paradigms(ieml_only = True) # list of the 53 strings of the root paradigms

    paradigm_dico2 = rank_usls(paradigms_list, usl_list2)
    #self.assertTrue(len(paradigm_dico2) == len(full_root_paradigms))
    #self.assertTrue(len(paradigm_dico2["E:E:F:."]) == 1)
    #self.assertTrue(paradigm_dico2["E:F:.M:M:.-"] == 2)