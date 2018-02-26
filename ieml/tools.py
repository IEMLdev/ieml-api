import xml.etree.ElementTree as ET
import random
import functools
from itertools import chain

from urllib.request import urlopen

from ieml.exceptions import CannotParse
from ieml.grammar.text import Text, text
from ieml.grammar.usl import Usl
from ieml.grammar.fact import Fact, fact
from ieml.grammar.parser import IEMLParser
from ieml.grammar.theory import Theory, theory
from ieml.grammar.topic import Topic, topic
from ieml.grammar.word import Word

from ieml.dictionary.version import get_default_dictionary_version
from .exceptions import InvalidIEMLObjectArgument
from .exceptions import CantGenerateElement
from .dictionary import Term, Dictionary


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
    def __init__(self, level=Theory, pool_size=20, dictionary_version=None):
        self.level = level
        self.pool_size = pool_size
        self.dictionary_version = dictionary_version

        if level > Text:
            raise ValueError('Cannot generate object higher than a Text.')

        self._build_pools()

        self.type_to_method = {
            Word: self.word,
            Topic: self.topic,
            Fact: self.fact,
            Theory: self.theory,
            Text: self.text
        }

    def _build_pools(self):
        """
        Slow method, retrieve all the terms from the database.
        :return:
        """
        if self.level >= Topic:
            # words
            self.topics_pool = set(self.topic() for i in range(self.pool_size))

        if self.level >= Fact:
            # sentences
            self.facts_pool = set(self.fact() for i in range(self.pool_size))

        if self.level >= Theory:
            self.theories_pool = set(self.theory() for i in range(self.pool_size))

        if self.level >= Text:
            self.propositions_pool = set(chain.from_iterable((self.topics_pool, self.facts_pool, self.theories_pool)))

        # self.hypertext_pool = set(self.hypertext() for i in range(self.pool_size))

    @_loop_result(10)
    def word(self):
        return Word(random.sample(Dictionary(self.dictionary_version).index, 1)[0])

    @_loop_result(10)
    def uniterm_topic(self):
        return topic([random.sample(Dictionary(self.dictionary_version).index, 1)])

    @_loop_result(10)
    def topic(self):
        return topic([Word(t) for t in random.sample(Dictionary(self.dictionary_version).index, 3)],
                     [Word(t) for t in random.sample(Dictionary(self.dictionary_version).index, 2)])

    def _build_graph_object(self, primitive, mode, max_nodes=6):
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

                result.add((s, a, m))
                break
        return result

    @_loop_result(10)
    def fact(self, max_clause=6):
        def p():
            return random.sample(self.topics_pool, 1)[0]

        return fact(self._build_graph_object(p, p, max_nodes=max_clause))

    @_loop_result(10)
    def theory(self, max_clause=4):
        def p():
            return random.sample(self.facts_pool, 1)[0]

        return theory(self._build_graph_object(p, p, max_nodes=max_clause))

    @_loop_result(10)
    def text(self):
        return text(random.sample(self.propositions_pool, random.randint(1, 8)))

    def from_type(self, type):
        try:
            return self.type_to_method[type]()
        except KeyError:
            raise ValueError("Can't generate that type or not an IEMLObject : %s"%str(type))


def list_bucket(url):
    root_node = ET.fromstring(urlopen(url).read())
    all_versions_entry = ({k.tag: k.text for k in list(t)} for t in root_node
                          if t.tag == '{http://s3.amazonaws.com/doc/2006-03-01/}Contents')

    # sort by date
    all_versions = sorted(all_versions_entry,
                          key=lambda t: t['{http://s3.amazonaws.com/doc/2006-03-01/}LastModified'], reverse=True)

    return [v['{http://s3.amazonaws.com/doc/2006-03-01/}Key'] for v in all_versions]


def ieml(arg, dictionary_version=None):
    if not dictionary_version:
        dictionary_version = get_default_dictionary_version()

    if isinstance(arg, Usl):
        if arg.dictionary_version != dictionary_version:
            arg.set_dictionary_version(dictionary_version)

        return arg

    if isinstance(arg, str):
        try:
            return IEMLParser(Dictionary(dictionary_version)).parse(arg)
        except CannotParse as e:
            raise InvalidIEMLObjectArgument(Usl, str(e))

    if isinstance(arg, Term):
        arg = Word(arg)
        if arg.dictionary_version != dictionary_version:
            arg.set_dictionary_version(dictionary_version)

        return arg

    raise NotImplemented