from ieml.AST import Term
from ieml.AST.propositions import Word, Morpheme, Clause, Sentence, SuperSentence, SuperClause, \
    AbstractAdditiveProposition, AbstractClause, AbstractProposition
from ieml.exceptions import CannotPromoteToLowerLevel, CannotDemoteProposition

terms_level_order = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]


class SentenceGraph:

    primitive_type = Word
    multiplicative_type = Clause
    additive_type = Sentence


class SuperSentenceGraph:

    primitive_type = Sentence
    multiplicative_type = SuperClause
    additive_type = SuperSentence

NULL_TERM = Term("E:")
NULL_MORPHEME = Morpheme([NULL_TERM])
NULL_WORD = Word(NULL_MORPHEME)
NULL_CLAUSE = Clause(NULL_WORD, NULL_WORD, NULL_WORD)
NULL_SENTENCE = Sentence([NULL_CLAUSE])
NULL_SUPERCLAUSE = SuperClause(NULL_SENTENCE, NULL_SENTENCE, NULL_SENTENCE)
NULL_SUPERSENTENCE = SuperSentence([NULL_SUPERCLAUSE])


def null_element(ast_level_type):
    """Returns the null element for the input ast_level_type"""
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


def promote_once(proposition):
    proposition_higher_type = terms_level_order[terms_level_order.index(proposition.__class__) + 1]
    result = None
    if issubclass(proposition_higher_type, AbstractAdditiveProposition):
        #  if the higher type is an additive proposition
        result = proposition_higher_type([proposition])
    elif issubclass(proposition_higher_type, AbstractClause):
        # if the higher type is a multiplicative proposition
        result = proposition_higher_type(proposition,
                                         null_element(type(proposition)),
                                         null_element(type(proposition)))

    elif issubclass(proposition_higher_type, Word):  # year, word is a bit special since it only has one child
        result = Word(proposition)
    result.check()
    return result


def promote_to(proposition, level_type):
    """Recursive function. Promotes a proposition to the type of level_type"""
    # TODO : do some type checking, like is it an abstract proposition or not, etc...
    if proposition.__class__ == level_type:
        # if the proposition is already at the right level, we just return it
        return proposition
    elif proposition.__class__ < level_type: # else, we have to raise it one level, and recurse.
        return promote_to(promote_once(proposition), level_type)
    elif proposition.__class__ > level_type:
        raise CannotPromoteToLowerLevel()


def demote_once(proposition):
    """Lowers the level of a proposition of 1 level.
    Supposed to be used on promoted propositions and/or additive propositions with only 1 element."""
    if isinstance(proposition, AbstractProposition):
        return proposition.children[0]
    else:
        raise CannotDemoteProposition()


def demote_to(proposition, level_type):
    """Recursive function. Demotes a proposition to a given level"""
    if type(proposition) < level_type:
        raise CannotDemoteProposition("Cannot demote to higher level!")
    elif isinstance(proposition, level_type):
        return proposition
    else:
        return demote_to(demote_once(proposition), level_type)


