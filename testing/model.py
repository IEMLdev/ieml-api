import models.base_queries

models.base_queries.DB_NAME = 'test_db'

from models.exceptions import RootParadigmMissing, RootParadigmIntersection
from ieml.operator import *
from models.terms.terms import TermsConnector
from models.relations.relations import RelationsConnector
from testing.helper import *


class TestModel(unittest.TestCase):
    def setUp(self):
        self.terms = TermsConnector()
        self.relations = RelationsConnector()

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
        self.terms.add_term(s1, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        try:
            self.terms.add_term(s2, {'FR': 'frd', 'EN': 'end'}, [], root=True)
        except Exception:
            self.assertRaises(RootParadigmIntersection)
        self.terms.remove_term(s1)

    def test_update(self):
        s1 = sc('F:')
        self.terms.add_term(s1, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        newt = {'FR': 'fr2', 'EN': 'en2'}
        self.terms.update_term(s1, tags=newt)
        self.assertEqual(self.terms.get_term(s1)['TAGS'], newt)
        self.terms.remove_term(s1)