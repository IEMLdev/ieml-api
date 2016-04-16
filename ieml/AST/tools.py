from ieml.exceptions import CannotPromoteToLowerLevel
from .propositions import Term, Word, Morpheme, Clause, Sentence, SuperSentence, SuperClause, \
    AbstractAdditiveProposition, AbstractClause

terms_level_order = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]

NULL_TERM = Term("E:")
NULL_MORPHEME = Morpheme([NULL_TERM])
NULL_WORD = Word(NULL_MORPHEME)
NULL_CLAUSE = Clause(NULL_WORD, NULL_WORD, NULL_WORD)
NULL_SENTENCE = Sentence([NULL_CLAUSE])
NULL_SUPERCLAUSE = SuperClause(NULL_SENTENCE, NULL_SENTENCE, NULL_SENTENCE)
NULL_SUPERSENTENCE = SuperSentence([NULL_SUPERCLAUSE])

def null_element(ast_level_type):
    null_elements_table = {
        Term : NULL_TERM,
        Morpheme : NULL_MORPHEME,
        Word : NULL_WORD,
        Clause : NULL_CLAUSE,
        Sentence : NULL_SENTENCE,
        SuperClause : NULL_SUPERCLAUSE,
        SuperSentence : NULL_SUPERSENTENCE
    }
    return null_elements_table[ast_level_type]


def promote_to(proposition, level_type):
    if proposition.__class__ == level_type:
        return proposition
    elif proposition.__class__ < level_type:
        proposition_higher_type = terms_level_order[terms_level_order.index(proposition.__class__) + 1]
        if issubclass(proposition_higher_type, AbstractAdditiveProposition):
            return promote_to(proposition_higher_type([proposition]),
                              level_type)
        elif issubclass(proposition_higher_type, AbstractClause):
            return promote_to(proposition_higher_type(proposition,
                                                      null_element(type(proposition)),
                                                      null_element(type(proposition))),
                              level_type)
        elif issubclass(proposition_higher_type, Word):
            return promote_to(Word(proposition),
                              level_type)
    elif proposition.__class__ > level_type:
        raise CannotPromoteToLowerLevel()
