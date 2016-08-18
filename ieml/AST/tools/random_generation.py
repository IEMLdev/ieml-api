import random

from helpers import Singleton
from ieml.AST import Morpheme, Term, Word, Clause, SuperClause, Sentence, SuperSentence
from ieml.AST.constants import MAX_NODES_IN_SENTENCE, MAX_NODES_IN_SUPERSENTENCE
from ieml.AST.tools import SentenceGraph, SuperSentenceGraph
from models.terms import get_random_terms


class RandomPropositionGenerator(metaclass=Singleton):

    def __init__(self):
        pass

    def _make_random_morpheme(self):
        term_count = random.randint(1, 3)
        return Morpheme([Term(term_ieml) for term_ieml in get_random_terms(term_count)])

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
            initial_nodes = [self._make_random_word()
                             for i in range(random.randint(3, MAX_NODES_IN_SENTENCE))]
            mode_nodes = [self._make_random_word() for i in range(len(initial_nodes))]
        else:
            initial_nodes = [self._make_random_sentence(Sentence)
                             for i in range(random.randint(3, MAX_NODES_IN_SUPERSENTENCE))]
            mode_nodes = [self._make_random_sentence(Sentence) for i in range(len(initial_nodes))]

        #preventing duplicated nodes (happens with sentences and clauses)
        for node in initial_nodes:
            node.check()
        initial_nodes = list(set(initial_nodes))

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

    def get_random_uniterm_word(self):
        """Returns a word with only one term in the morpheme's substance, and that's it"""
        return Word(Morpheme([Term(term_ieml) for term_ieml in get_random_terms(1)]))

    def get_random_multiterm_word(self):
        """Returns a word that is specifically not a uniterm word
        (ie non empyt mode or sevelral elements in the substance)"""
        if bool(random.getrandbits(1)):
            # no mode
            return Word(Morpheme([Term(term_ieml) for term_ieml in get_random_terms(random.randint(2,3))]))
        else:
            # existent mode
            return Word(self._make_random_morpheme(), self._make_random_morpheme())


class BulkUSLGenerator:

    def __init__(self, term_pool_page_size=100):
        self.page_size = term_pool_page_size
        self.terms_pool = []

    def _get_random_terms(self, count=1):
        current_pool_count = self.terms_pool
        if count >= len(self.terms_pool):
            # pull more terms from the DB, then shuffle them
            self.terms_pool += [Term(term_ieml) for term_ieml in get_random_terms(self.page_size)]

        # updating the pool to a slice, and returning the end slice
        # [----------------that slice we keep--------------|----that slice is return'd----]
        output_slice = self.terms_pool[current_pool_count - count, current_pool_count]
        self.terms_pool = self.terms_pool[0:current_pool_count - count]
        return output_slice
