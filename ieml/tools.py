import random
import itertools
import functools

from .commons import IEMLObjects
from .exceptions import InvalidIEMLObjectArgument
from .syntax.parser.parser import IEMLParser
from .syntax import Sentence, Clause, SuperSentence, SuperClause, Text, Word, Morpheme
from .exceptions import CantGenerateElement
from .dictionary import Term, Dictionary


def ieml(arg):
    if isinstance(arg, IEMLObjects):
        return arg

    if isinstance(arg, str):
        return IEMLParser().parse(arg)

    raise ValueError("Invalid argument, c'ant instantiate an IEMLObject from %s."%str(arg))


def _loop_result(max_try):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ex = None
            for i in range(max_try):
                try:
                    return func(*args, **kwargs)
                except InvalidIEMLObjectArgument as e:
                    ex = e
                    continue

            raise CantGenerateElement(str(ex))
        return wrapper
    return decorator


class RandomPoolIEMLObjectGenerator:
    def __init__(self, level=Text, pool_size=20):
        self.level = level
        self.pool_size = pool_size

        if level > Text:
            raise ValueError('Cannot generate object higher than a Text.')

        self._build_pools()

        self.type_to_method = {
            Term: self.term,
            Word: self.word,
            Sentence: self.sentence,
            SuperSentence: self.super_sentence,
            Text: self.text
        }

    def _build_pools(self):
        """
        Slow method, retrieve all the terms from the database.
        :return:
        """
        if self.level >= Word:
            # words
            self.words_pool = set(self.word() for i in range(self.pool_size))

        if self.level >= Sentence:
            # sentences
            self.sentences_pool = set(self.sentence() for i in range(self.pool_size))

        if self.level >= SuperSentence:
            self.super_sentences_pool = set(self.super_sentence() for i in range(self.pool_size))

        if self.level >= Text:
            self.propositions_pool = set(itertools.chain.from_iterable((self.words_pool, self.sentences_pool, self.super_sentences_pool)))

        # self.hypertext_pool = set(self.hypertext() for i in range(self.pool_size))

    @_loop_result(10)
    def term(self):
        return random.sample(Dictionary().index, 1)[0]

    @_loop_result(10)
    def uniterm_word(self):
        return Word(Morpheme(random.sample(Dictionary().index, 1)))

    @_loop_result(10)
    def word(self):
        return Word(Morpheme(random.sample(Dictionary().index, 3)), Morpheme(random.sample(Dictionary().index, 2)))

    def _build_graph_object(self, primitive, mode, object, max_nodes=6):
        nodes = {primitive()}
        modes = set()

        if max_nodes < 2:
            raise ValueError('Max nodes >= 2.')

        result = set()

        for i in range(random.randint(2, max_nodes)):
            while True:
                s, a, m = random.sample(nodes, 1)[0], primitive(), mode()
                if a in nodes or m in nodes or a in modes:
                    continue

                nodes.add(a)
                modes.add(m)

                result.add(object(s, a, m))
                break
        return result

    @_loop_result(10)
    def sentence(self, max_clause=6):
        def p():
            return random.sample(self.words_pool, 1)[0]

        return Sentence(self._build_graph_object(p, p, Clause, max_nodes=max_clause))

    @_loop_result(10)
    def super_sentence(self, max_clause=4):
        def p():
            return random.sample(self.sentences_pool, 1)[0]

        return SuperSentence(self._build_graph_object(p, p, SuperClause, max_nodes=max_clause))

    @_loop_result(10)
    def text(self):
        return Text(random.sample(self.propositions_pool, random.randint(1, 8)))

    def from_type(self, type):
        try:
            return self.type_to_method[type]()
        except KeyError:
            raise ValueError("Can't generate that type or not an IEMLObject : %s"%str(type))