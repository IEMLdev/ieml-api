from ieml.ieml_objects import Term, Word, Sentence, SuperSentence, Text, Hypertext
from ieml.script.tables import generate_tables
from ieml.script.operator import sc
from collections import namedtuple, defaultdict
from ieml.script.constants import AUXILIARY_CLASS, VERB_CLASS, NOUN_CLASS
from models.terms import TermsConnector
from models.relations.relations import RelationsConnector
import bidict
import numpy as np

ScoreNode = namedtuple('ScoreNode', ['script', 'score'])
Cache = namedtuple('Cache', ['source_layer', 'source_class', 'source_usl', 'usl_index'])
ParadigmMetadata = namedtuple('ParadigmMetadata', ['paradigm', 'score', 'nouns', 'auxiliary', 'verb'])


def _build_cache(usl_collection):

    def usl_elem_generator(u):
        if isinstance(u, (Word, Sentence, SuperSentence)):
            yield u
        elif isinstance(u, (Text, Hypertext)):
            for c in u.children:
                yield from usl_elem_generator(c)

    # For every term we associate a vector where each coordinate is the number of citations from a given layer
    # First coordinate: SuperSentence
    # Second coordinate: Sentence
    # Third coordinate: Word
    source_layer = defaultdict(lambda: [0, 0, 0])
    # For every term we associate a vector where each coordinate
    # is the number of citations from a given grammatical class
    source_class = defaultdict(lambda: [0, 0, 0])
    # Each term will be mapped to a vector indicating the number of citations from an usl in the usl_collection
    # each usl is given a coordinate in the usl_index bidict
    source_usl = defaultdict(lambda: [0 for u in usl_collection])
    # Every usl is given a coordinate for vector representation
    usl_index = bidict.bidict({i: u for i, u in enumerate(usl_collection)})

    for u in usl_collection:
        for elem in usl_elem_generator(u):
            terms = [term for term in elem.tree_iter() if isinstance(term, Term)]
            for t in terms:
                # TODO: Maybe use string representation of terms so that we don't need to worry about Terms/Script
                source_layer[t.script][coordinate[elem.__class__]] += 1
                source_class[t.script][elem.grammatical_class] += 1
                source_usl[t.script][usl_index.inv[u]] += layer_weight[elem.__class__]

                # We also count all the contained terms
                rc = RelationsConnector()
                term_rel = rc.get_script(t.script)
                if 'CONTAINS' in term_rel['RELATIONS']:
                    for child in term_rel['RELATIONS']['CONTAINS']:
                        child_script = sc(child)
                        source_layer[child_script][coordinate[elem.__class__]] += 1
                        source_class[child_script][elem.grammatical_class] += 1
                        source_usl[child_script][usl_index.inv[u]] += layer_weight[elem.__class__]


    return Cache(source_layer=source_layer, source_class=source_class, source_usl=source_usl, usl_index=usl_index.inv)


_cache = None


def rank_paradigms(paradigm_list, usl_collection):
    """
    Paradigms should be of type Script ***NOT TYPE Term***

    Parameters
    ----------
    paradigm_list
    usl_collection

    Returns
    -------

    """

    # TODO: So check and convert Term types to Script type
    result = []
    global _cache
    if not _cache:
        _cache = _build_cache(usl_collection)

    for paradigm in paradigm_list:

        score = (_cache.source_layer[paradigm][0] * layer_weight[SuperSentence] +
                 _cache.source_layer[paradigm][1] * layer_weight[Sentence] +
                 _cache.source_layer[paradigm][2] * layer_weight[Word])

        result.append(ParadigmMetadata(paradigm=paradigm, score=score,
                                       nouns=_cache.source_class[paradigm][NOUN_CLASS],
                                       auxiliary=_cache.source_class[paradigm][AUXILIARY_CLASS],
                                       verb=_cache.source_class[paradigm][VERB_CLASS]))

    return sorted(result, key=lambda x: x.score, reverse=True)


def rank_usls(term_list, usl_collection):
    """
    This method assumes the user will correctly giv it a list of root paradigms or of normal terms
    Parameters

    Paradigms should be of type Script ***NOT TYPE Term***
    ----------
    term_list: A list of terms, can be ROOT paradigms or plain old terms
    usl_collection

    Returns
    -------
    A dictionary that maps for each root paradigm a sorted list of USLs based on the number of citations
    """

    # TODO: So check and convert Term types to Script type

    global _cache
    if not _cache:
        _cache = _build_cache(usl_collection)

    return {term: sorted(usl_collection, key=lambda u: _cache.source_usl[term][_cache.usl_index[u]], reverse=True)
            for term in term_list}


def paradigm_usl_distribution(paradigm, usl_collection):
    """

    Parameters
    ----------
    paradigm
    usl_collection

    Returns
    -------
    Distribution of number of terms (contained in 'paradigm') cited overlaid on the paradigms table
    """

    global _cache
    if not _cache:
        _cache = _build_cache(usl_collection)

    if isinstance(paradigm, str):
        paradigm = sc(paradigm)

    tbls = generate_tables(paradigm)
    dist_tables = [np.zeros(table.cells.shape, dtype=int) for table in tbls]

    for tbl_idx, table in enumerate(tbls):
        it = np.nditer(table.cells, flags=['multi_index', 'refs_ok'])
        while not it.finished:
            # it[0] is the cell element
            dist_tables[tbl_idx][it.multi_index] += sum(_cache.source_layer[it[0].item()])
            it.iternext()

        # # We also want to count the cell citations coming from the headers
        # if table.dimension == 1:
        #     for i, row_header in enumerate(table.headers[0]):
        #         dist_tables[tbl_idx][i] += sum(_cache.source_layer[row_header])
        # elif table.dimension == 2:
        #     for i, row_header in enumerate(table.headers[0]):
        #         dist_tables[tbl_idx][i, :] += sum(_cache.source_layer[row_header])
        #     for i, col_header in enumerate(table.headers[1]):
        #         dist_tables[tbl_idx][:, i] += sum(_cache.source_layer[col_header])
        # elif table.dimension == 3:
        #     for i, row_header in enumerate(table.headers[0]):
        #         dist_tables[tbl_idx][i, :, :] += sum(_cache.source_layer[row_header])
        #     for i, col_header in enumerate(table.headers[1]):
        #         dist_tables[tbl_idx][:, i, :] += sum(_cache.source_layer[col_header])
        #     for i, tab_header in enumerate(table.headers[2]):
        #         dist_tables[tbl_idx][:, :, i] += sum(_cache.source_layer[tab_header])

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