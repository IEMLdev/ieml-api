import importlib
import random
import types
import unittest
from collections import namedtuple
from functools import partial
from string import ascii_lowercase
from types import ModuleType

import sys
import config
from ieml.script.operator import sc
from models.constants import TAG_LANGUAGES
from models.relations.relations import RelationsConnector
from models.terms.terms import TermsConnector
from models.usls.usls import USLConnector


def stub_db(module_model, connectors):
    config.DB_NAME = 'test_db'
    if isinstance(module_model, str):
        module_model = sys.modules[module_model]
    reload_model_package(module_model, reloaded=set(), seen=set(), connectors=connectors)
    print('switching to test_db.')


def normal_db(module_model, connectors):
    importlib.reload(config)
    if isinstance(module_model, str):
        module_model = sys.modules[module_model]

    reload_model_package(module_model, reloaded=set(), seen=set(), connectors=connectors)
    print('resetting to normal db (ieml_db). module reloaded ')


def _dependencies(module):
    return {g.__module__ if isinstance(g, type) else g.__name__
            for g in module.__dict__.values() if isinstance(g, type) or isinstance(g, ModuleType)}


def reload_model_package(module, reloaded, seen, connectors):

    to_reload = {__name__}
    for m in sys.modules.keys():
        p = m.split('.')
        if len(p) == 1 and p[0] == 'models':
            to_reload.add(m)
        if len(p) > 1 and p[1] in connectors:
            to_reload.add(m)

    if module in seen:
        raise ValueError('Circular dependency : %s'%module.__name__)
    seen.add(module)

    deps = (_dependencies(module) & to_reload) - ({module.__name__} | reloaded)

    while deps:
        m = next(iter(deps))
        reloaded |= (reload_model_package(sys.modules[m], reloaded=reloaded, seen=seen, connectors=connectors))
        deps = (_dependencies(module) & to_reload) - ({module.__name__} | reloaded)

    importlib.reload(module)
    reloaded.add(module.__name__)
    return reloaded

model_test_cases = {}
_index = 0


def _get_model_test_cases(connectors):
    if connectors in model_test_cases:
        return model_test_cases[connectors]

    global _index
    test_case = types.new_class('ModelTestCase'+str(_index), (ModelTestCase,), {})
    _index += 1

    test_case.connectors = connectors

    model_test_cases[connectors] = test_case

    return test_case


def modelTestCase(kind=None):
    connectors = ()
    if kind == 'terms':
        connectors = ('terms', 'relations')
    if kind == 'usls':
        connectors = ('usls',)

    return _get_model_test_cases(connectors)


class ModelTestCase(unittest.TestCase):
    def __init__(self, test_name='runTest'):
        if not hasattr(self.__class__, 'connectors'):
            self.__class__.connectors = []
        super().__init__(test_name)

    @classmethod
    def setUpClass(cls):
        stub_db(cls.__module__, cls.connectors)

    @classmethod
    def tearDownClass(cls):
        normal_db(cls.__module__, cls.connectors)

    def setUp(self):
        self.terms = TermsConnector()
        self.relations = RelationsConnector()
        self.usls = USLConnector()

        self._clear()

    def _clear(self):
        if 'terms' in self.connectors:
            self.terms.drop()
        if 'relations' in self.connectors:
            self.relations.drop()
        if 'usls' in self.connectors:
            self.usls.drop()

    def _save_paradigm(self, paradigm, recompute_relations=True):
        list_terms = [{
                          'AST': s,
                          'ROOT': False,
                          'TAGS': _tag(),
                          'INHIBITS': [],
                          'METADATA': {}
                      } for s in paradigm.paradigms]

        list_terms.append({
            'AST': paradigm.root,
            'ROOT': True,
            'TAGS': _tag(),
            'INHIBITS': [],
            'METADATA': {}
        })
        self.terms.save_multiple_terms(list_terms, recompute_relations=recompute_relations)

    def _count(self):
        return self.terms.terms.find().count() + self.relations.relations.find().count()

def _tag():
    return {l: ''.join(random.sample(ascii_lowercase, 20)) for l in TAG_LANGUAGES}


Paradigm = namedtuple('Paradigm', ['root', 'paradigms'])
paradigms = {
    0: Paradigm(root=sc('F:F:.O:.M:.-'), paradigms={sc('T:M:.O:.M:.-'), sc('F:M:.O:.M:.-'), sc('T:U:.O:.M:.-')}),
    1: Paradigm(root=sc('O:O:.O:O:.-'), paradigms=set(map(sc, ['O:O:.wo.-', 'wu.O:O:.-', 'wa.O:O:.-', 'wo.O:O:.-', 'O:O:.we.-', 'we.O:O:.-', 'O:O:.wa.-', 'O:O:.wu.-', 'wo.U:O:.-', 'wo.A:O:.-', 'wo.O:U:.-', 'wo.O:A:.-', 'wa.U:O:.-', 'wa.A:O:.-', 'wa.O:U:.-', 'wa.O:A:.-', 'wu.U:O:.-', 'wu.A:O:.-', 'wu.O:U:.-', 'wu.O:A:.-', 'we.U:O:.-', 'we.A:O:.-', 'we.O:U:.-', 'we.O:A:.-', 'U:O:.wo.-', 'A:O:.wo.-', 'O:U:.wo.-', 'O:A:.wo.-', 'U:O:.wa.-', 'A:O:.wa.-', 'O:U:.wa.-', 'O:A:.wa.-', 'U:O:.wu.-', 'A:O:.wu.-', 'O:U:.wu.-', 'O:A:.wu.-', 'U:O:.we.-', 'A:O:.we.-', 'O:U:.we.-', 'O:A:.we.-'])))
}


if __name__ == '__main__':
    o = modelTestCase()()
    str(o)


    # import models.relations
    # old = sys.modules['models.base_queries'].__dict__['DB_NAME']
    # print(old)
    # stub_db(sys.modules['models.relations.relations_queries'])
    # # importlib.reload(old)
    # new = sys.modules['models.base_queries'].__dict__['DB_NAME']
    # print(new)
    # print(old is new)
    # importlib.reload(sys.modules['models.relations.relations_queries'])




