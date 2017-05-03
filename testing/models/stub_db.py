import importlib
import random
import unittest
from collections import namedtuple
from string import ascii_lowercase
from types import ModuleType

import sys
import config
from ieml.script.operator import sc
from models.constants import TAG_LANGUAGES
from models.intlekt.edition.glossary import GlossaryConnector
from models.relations.relations import RelationsConnector
from models.templates.templates import TemplatesConnector
from models.terms.terms import TermsConnector
from models.usls.usls import USLConnector


def stub_db(module_model, connectors):
    """
    Stub the connectors to the db. The connectors to non stubbed connectors must have been previousely instantiated.
    After the call to this function, all the connectors instantiated that are in the connectors argument will be
    stubbed.
    :param module_model: the module that will use the stubbed connectors.
    :param connectors: the connectors to stub.
    :return: None
    """
    if not connectors:
        return

    config.DB_NAME = 'test_db'
    config.DB_USERS = 'test_users'

    if isinstance(module_model, str):
        module_model = sys.modules[module_model]
    reloaded = reload_model_package(module_model, reloaded=set(), seen=set(), connectors=connectors)
    print('switching to test_db. (' + ', '.join(reloaded)+')')


def normal_db(module_model, connectors):
    """
    Restore the connectors to use a normal db. (ieml_db)
    :param module_model: the stubbed module
    :param connectors: the connector to restore
    :return: None
    """
    if not connectors:
        return

    importlib.reload(config)
    if isinstance(module_model, str):
        module_model = sys.modules[module_model]

    reload_model_package(module_model, reloaded=set(), seen=set(), connectors=connectors)
    print('resetting to normal db (ieml_db). module reloaded ')


def _dependencies(module):
    return {g.__module__ if isinstance(g, type) else g.__name__
            for g in module.__dict__.values() if isinstance(g, type) or isinstance(g, ModuleType)}


def reload_model_package(module, reloaded, seen, connectors):
    """
    Reload the module and all the dependencies in the models package.
    :param module:
    :param reloaded:
    :param seen:
    :param connectors:
    :return:
    """
    to_reload = {__name__}
    for m in sys.modules.keys():
        p = m.split('.')
        if p[0] != 'models':
            continue
        if len(p) == 1:
            # the model package
            to_reload.add(m)
        if len(p) == 2 and not hasattr(sys.modules[m], '__path__'):
            # direct module in the model package
            to_reload.add(m)
        if len(p) >= 2 and p[1] in connectors:
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


class ModelTestCase(unittest.TestCase):
    """
    The Test case that stub the db before executing the test. The connectors that must be stubbed should be specified
      as a class attribute connectors:

    connectors = ('terms', 'relations') # stubb the terms and relations connectors
    """

    # default stub to no class, must override the property in child class
    connectors = tuple()

    def __init__(self, test_name='runTest'):
        if not hasattr(self.__class__, 'connectors'):
            self.__class__.connectors = []
        super().__init__(test_name)

        # init all the connectors (to instantiate all non stubbed connectors, otherwise, if we instanciate for the 1st
        # time a non stubbed connector after the stubbing of the other connector, it will be stubbed)
        # because of the stub of the singleton DbConnector in models.commons
        self.terms = TermsConnector()
        self.relations = RelationsConnector()
        self.usls = USLConnector()
        self.templates = TemplatesConnector()
        self.glossary = GlossaryConnector()

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
        self.templates = TemplatesConnector()
        self.glossary = GlossaryConnector()
        self._clear()

    def _clear(self):
        if 'terms' in self.connectors:
            self.terms.drop()
        if 'relations' in self.connectors:
            self.relations.drop()
        if 'usls' in self.connectors:
            self.usls.drop()
        if 'logins' in self.connectors:
            from models.logins.logins import _get_users_collection
            _get_users_collection().drop()
        if 'templates' in self.connectors:
            self.templates.drop()
        if 'glossary' in self.connectors:
            self.glossary.drop()

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



