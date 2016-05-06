import random

from ieml.AST.constants import MAX_TERMS_IN_MORPHEME, MAX_NODES_IN_SENTENCE
from ieml.exceptions import CannotPromoteToLowerLevel
from .propositions import Term, Word, Morpheme, Clause, Sentence, SuperSentence, SuperClause, \
    AbstractAdditiveProposition, AbstractClause
from helpers import Singleton
from models import DictionaryQueries

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


def promote_to(proposition, level_type):
    """Recursive function that promotes a proposition to the type of level_type"""
    if proposition.__class__ == level_type:
        return proposition
    elif proposition.__class__ < level_type:
        result = None
        proposition_higher_type = terms_level_order[terms_level_order.index(proposition.__class__) + 1]
        if issubclass(proposition_higher_type, AbstractAdditiveProposition):
            result = promote_to(proposition_higher_type([proposition]),
                              level_type)
        elif issubclass(proposition_higher_type, AbstractClause):
            result = promote_to(proposition_higher_type(proposition,
                                                      null_element(type(proposition)),
                                                      null_element(type(proposition))),
                              level_type)
        elif issubclass(proposition_higher_type, Word):
            result = promote_to(Word(proposition),
                              level_type)

        result.check()
        return result
    elif proposition.__class__ > level_type:
        raise CannotPromoteToLowerLevel()


class RandomPropositionGenerator(metaclass=Singleton):

    def __init__(self):
        self.db = DictionaryQueries()

    def _make_random_morpheme(self):
        term_count = random.randint(1, 3)
        return Morpheme([Term(term_ieml) for term_ieml in self.db.get_random_terms(term_count)])

    def _make_random_word(self):

        if bool(random.getrandbits(1)) :
            return Word(self._make_random_morpheme())
        else:
            return Word(self._make_random_morpheme(), self._make_random_morpheme())

    def _make_random_clause(self, type):
        """Returns a random clause/superclause depending on type"""
        # hehe used a tuple comprehension instead of explicitly calling the function 3 times
        # you can't handle my pythonic craftsmanship
        if type == Clause:
            return Clause(*(self._make_random_word() for i in range(3)))
        else:
            return SuperClause(*(self._make_random_sentence(Sentence) for i in range(3)))

    def _make_random_sentence(self, type):
        """Returns a random sentence/supersentence depending on type"""
        # this builds an actual sentence tree, since if we just make random clause, it will almost always fail
        # to make a correct sentence. It makes a tree with up to 4 children for each node

        graph_type = SentenceGraph if type == Sentence else SuperSentenceGraph

        # first,  generating the nodes
        if type is Sentence:
            initial_nodes = [self._make_random_word() for i in range(random.randint(3, MAX_NODES_IN_SENTENCE))]
            mode_nodes = [self._make_random_word() for i in range(len(initial_nodes))]
        else:
            initial_nodes = [self._make_random_sentence(Sentence) for i in range(random.randint(3, MAX_NODES_IN_SENTENCE))]
            mode_nodes = [self._make_random_sentence(Sentence) for i in range(len(initial_nodes))]

        # then, constructing a tree using a priority queue (current_parents)
        clauses_list = []
        current_parents = [initial_nodes.pop(0)]
        while current_parents:
            current_parent = current_parents.pop()
            for i in range(random.randint(1,4)):
                try:
                    child_node = initial_nodes.pop()
                    mode_node = mode_nodes.pop()
                except IndexError:
                    break

                # instantiating either a clause or super clause with the current parent and a new child node
                clauses_list.append(graph_type.multiplicative_type(current_parent, child_node, mode_node))
                current_parents.append(child_node)

        return type(clauses_list)


    def get_random_proposition(self, ast_type):
        """Returns an unchecked, unordered (but hopefully correct) proposition of level ast_type"""
        result = None
        if ast_type is Morpheme:
            result = self._make_random_morpheme()
        elif ast_type is Word:
            result = self._make_random_word()
        elif ast_type in [Sentence, SuperSentence]:
            result = self._make_random_sentence(ast_type)
        else:
            result = self._make_random_clause(ast_type)

        result.check()
        result.order()

        return result
