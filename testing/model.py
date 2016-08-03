import random
from collections import namedtuple
from string import ascii_lowercase

import models.base_queries

models.base_queries.DB_NAME = 'test_db'

from models.exceptions import RootParadigmMissing, RootParadigmIntersection, InvalidTags, DuplicateTag
from ieml.operator import *
from models.terms.terms import TermsConnector
from models.relations.relations import RelationsConnector
from models.base_queries import DBConnector
from models.constants import TERMS_COLLECTION, SCRIPTS_COLLECTION, TAG_LANGUAGES
from scripts import load_old_db
from testing.helper import *


def _tag():
    return {l: ''.join(random.sample(ascii_lowercase, 20)) for l in TAG_LANGUAGES}

Paradigm = namedtuple('Paradigm', ['root', 'paradigms'])
paradigms = {
    0: Paradigm(root=sc('F:F:.O:.M:.-'), paradigms={sc('T:M:.O:.M:.-'), sc('F:M:.O:.M:.-'), sc('T:U:.O:.M:.-')})
}

class TestModel(unittest.TestCase):
    def setUp(self):
        self.terms = TermsConnector()
        self.relations = RelationsConnector()

    def _clear(self):
        self.terms.terms.drop()
        self.relations.relations.drop()

    def test_insert_term(self):
        script = sc("M:M:M:.U:U:U:.e.-")
        self.terms.add_term(script, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        self.assertTrue(self.terms.get_term(str(script))['_id'] == "M:M:M:.U:U:U:.e.-")
        self.terms.remove_term(script)

    def test_insert_multiple_term(self):
        root = sc('O:M:M:.')
        self.terms.add_term(root, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        for i, s in enumerate(root.singular_sequences):
            self.terms.add_term(s, {'FR': 'fr'+str(i), 'EN': 'en'+str(i)}, [])
        p = sc('O:M:S:.')
        self.terms.add_term(p, {'FR': 'frp', 'EN': 'enp'}, [])

        self.terms.remove_term(p)
        for s in root.singular_sequences:
            self.terms.remove_term(s)
        self.terms.remove_term(root)

        self.assertEqual(list(self.terms.get_all_terms()), [])

    def test_fail_no_root(self):
        s = sc('A:')
        try:
            self.terms.add_term(s, {'FR': 'fr', 'EN': 'en'}, [])
        except Exception:
            self.assertRaises(RootParadigmMissing)

    def test_fail_paradigm_intersect(self):
        s1 = sc('M:')
        s2 = sc('F:')
        self.terms.add_term(s1, _tag(), [], root=True)
        with self.assertRaises(RootParadigmIntersection):
            self.terms.add_term(s2, _tag(), [], root=True)

        self._clear()

    def test_update(self):
        s1 = sc('F:')
        self.terms.add_term(s1, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        newt = {'FR': 'fr2', 'EN': 'en2'}
        self.terms.update_term(s1, tags=newt)
        self.assertEqual(self.terms.get_term(s1)['TAGS'], newt)
        self.terms.remove_term(s1)

    def test_remove_root_paradigm(self):
        self._clear()

        paradigm = paradigms[0]
        self._save_paradigm(paradigm)

        self.terms.remove_term(paradigm.root, remove_roots_child=True)
        self.assertTrue(self.terms.get_all_terms().count() == 0,
                        msg='Delete of root paradigm have not remove subsequent paradigms.')

    def test_tag(self):
        self._clear()
        with self.assertRaises(InvalidTags, msg='Term saved with an empty tag.'):
            self.terms.add_term(sc('M:'), tags={}, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with missing languages.'):
            self.terms.add_term(sc('M:'), tags={'FR':'fdsas'}, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with an unknown language.'):
            self.terms.add_term(sc('M:'), tags={'QW': 'dsadsa'}, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with tag of incompatible type.'):
            self.terms.add_term(sc('M:'), tags={
                'FR': ('f', 'e', 'e'),
                'EN': ()
            }, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        tag = _tag()

        self.terms.add_term(sc('M:'), tags=tag, root=True, inhibits=[])

        with self.assertRaises(DuplicateTag, msg='Term saved with duplicate tag.'):
            self.terms.add_term(sc('O:'), tags=tag, root=True, inhibits=[])

        self._clear()

    def test_search_by_tag(self):
        self._clear()
        tag = _tag()
        self.terms.add_term(sc('M:'), tag, [], root=True)
        self.assertTrue(self.terms.search_by_tag(tag['EN'], 'EN').count() == 1)

    def test_rank(self):
        self._clear()
        paradigm = paradigms[0]
        self._save_paradigm(paradigm)


    def _save_paradigm(self, paradigm):
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
        self.terms.save_multiple_terms(list_terms)

    def _count(self):
        return self.terms.terms.find().count() + self.relations.relations.find().count()